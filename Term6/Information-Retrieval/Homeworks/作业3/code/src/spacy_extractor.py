"""
spaCy Matcher 抽取器 (L2)：
基于 token 属性（POS、LEMMA、DEP）的规则匹配，比纯正则更具语言学感知能力。
"""

from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc

from src.parser import Document
from src.base_extractor import BaseExtractor
from src.schema import AcademicPaperEvent, MetricResult
from src.nlp_pipeline import get_nlp


# 常见学术数据集名称（用于 PhraseMatcher）
KNOWN_DATASETS = [
    "MNIST", "CIFAR-10", "CIFAR-100", "ImageNet", "COCO", "SQuAD",
    "GLUE", "SuperGLUE", "WMT", "Penn Treebank", "SST-2", "IMDB",
    "Yelp", "SNLI", "MultiNLI", "CoNLL", "OntoNotes", "WikiText",
    "MS MARCO", "TREC", "Reuters", "20 Newsgroups",
    "AGNews", "DBpedia", "Amazon Reviews", "Europarl",
]

# 常见方法名（用于 PhraseMatcher）
KNOWN_METHODS = [
    "linear regression", "logistic regression", "random forest",
    "gradient boosting", "support vector machine", "SVM",
    "deep learning", "neural network", "convolutional neural network", "CNN",
    "recurrent neural network", "RNN", "LSTM", "GRU",
    "transformer", "BERT", "GPT", "attention mechanism",
    "k-means", "PCA", "t-SNE", "decision tree",
    "naive Bayes", "XGBoost", "LightGBM", "CatBoost",
    "generative adversarial network", "GAN",
    "variational autoencoder", "VAE",
    "reinforcement learning", "transfer learning",
    "difference-in-differences", "regression discontinuity",
    "instrumental variables", "propensity score matching",
    "OLS", "2SLS", "GMM", "fixed effects", "random effects",
    "meta-analysis", "structural equation modeling",
    "Bayesian", "Monte Carlo", "bootstrapping",
    "grounded theory", "content analysis", "thematic analysis",
]


def _dedup(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


class SpacyExtractor(BaseExtractor):
    """spaCy Matcher 抽取器 (L2)。"""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._model_name = model_name
        self._nlp = None
        self._matcher = None
        self._phrase_matcher_datasets = None
        self._phrase_matcher_methods = None

    def _ensure_loaded(self):
        """懒加载 spaCy 模型和 Matcher。"""
        if self._nlp is not None:
            return
        # Matcher 规则不依赖 NER，禁用可减少模型内存占用。
        self._nlp = get_nlp(self._model_name, disable=("ner",))
        self._setup_matcher()
        self._setup_phrase_matchers()

    def _setup_matcher(self):
        """配置 token 级别的 Matcher 规则。"""
        self._matcher = Matcher(self._nlp.vocab)

        # 方法模式："using/employ/apply [DET?] [NOUN+]"
        self._matcher.add("METHOD_VERB", [
            [
                {"LEMMA": {"IN": ["use", "employ", "apply", "adopt", "implement", "leverage"]}},
                {"POS": "DET", "OP": "?"},
                {"POS": {"IN": ["ADJ", "NOUN", "PROPN"]}, "OP": "+"},
            ],
        ])

        # 提议模式："propose/introduce [DET?] [ADJ?] [NOUN+]"
        self._matcher.add("METHOD_PROPOSE", [
            [
                {"LEMMA": {"IN": ["propose", "introduce", "develop", "present", "design"]}},
                {"POS": "DET", "OP": "?"},
                {"POS": "ADJ", "OP": "?"},
                {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"},
            ],
        ])

        # 数据集模式："dataset/corpus [of/called] [PROPN+]"
        self._matcher.add("DATASET_LABEL", [
            [
                {"LEMMA": {"IN": ["dataset", "corpus", "benchmark", "data"]}},
                {"LEMMA": {"IN": ["of", "called", "named", "from"]}, "OP": "?"},
                {"POS": {"IN": ["PROPN", "NOUN"]}, "OP": "+"},
            ],
        ])

        # 发现模式："find/show/demonstrate that ..."
        self._matcher.add("FINDING_THAT", [
            [
                {"LEMMA": {"IN": [
                    "find", "show", "demonstrate", "reveal", "suggest",
                    "indicate", "confirm", "conclude", "observe",
                ]}},
                {"LOWER": "that"},
            ],
        ])

        # 结果模式："significantly [VERB] ..."
        self._matcher.add("FINDING_SIGNIFICANT", [
            [
                {"LOWER": {"IN": [
                    "significantly", "positively", "negatively", "substantially",
                ]}},
                {"POS": "VERB"},
            ],
        ])

    def _setup_phrase_matchers(self):
        """配置 PhraseMatcher 用于已知名称列表。"""
        self._phrase_matcher_datasets = PhraseMatcher(self._nlp.vocab, attr="LOWER")
        patterns = [self._nlp.make_doc(name) for name in KNOWN_DATASETS]
        self._phrase_matcher_datasets.add("KNOWN_DS", patterns)

        self._phrase_matcher_methods = PhraseMatcher(self._nlp.vocab, attr="LOWER")
        patterns = [self._nlp.make_doc(name) for name in KNOWN_METHODS]
        self._phrase_matcher_methods.add("KNOWN_METHOD", patterns)

    @property
    def name(self) -> str:
        return "spacy_matcher"

    def extract(self, doc: Document) -> AcademicPaperEvent:
        self._ensure_loaded()

        text = doc.full_text
        if not text:
            return AcademicPaperEvent(
                doc_id=doc.doc_id, title=doc.title, doi=doc.doi, extraction_method=self.name
            )

        max_chars = self._nlp.max_length
        if len(text) > max_chars:
            text = text[:max_chars]
        spacy_doc = self._nlp(text)

        methods = self._extract_methods(spacy_doc)
        datasets = self._extract_datasets(spacy_doc)
        findings = self._extract_findings(spacy_doc)

        return AcademicPaperEvent(
            doc_id=doc.doc_id,
            title=doc.title,
            doi=doc.doi,
            methods=methods,
            datasets=datasets,
            findings=findings,
            extraction_method=self.name,
        )

    def _extract_methods(self, doc: Doc) -> list[str]:
        results = []

        # PhraseMatcher: 已知方法名
        matches = self._phrase_matcher_methods(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            results.append(span.text)

        # Token Matcher: 动词引导的方法模式
        matches = self._matcher(doc)
        for match_id, start, end in matches:
            label = self._nlp.vocab.strings[match_id]
            if label in ("METHOD_VERB", "METHOD_PROPOSE"):
                span = doc[start:end]
                # 跳过动词本身，取后续名词短语
                method_tokens = [t for t in span if t.pos_ in ("NOUN", "PROPN", "ADJ")]
                if method_tokens:
                    method = " ".join(t.text for t in method_tokens)
                    if len(method) > 2:
                        results.append(method)

        return _dedup(results)[:15]

    def _extract_datasets(self, doc: Doc) -> list[str]:
        results = []

        # PhraseMatcher: 已知数据集名
        matches = self._phrase_matcher_datasets(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            results.append(span.text)

        # Token Matcher: 句法模式
        matches = self._matcher(doc)
        for match_id, start, end in matches:
            label = self._nlp.vocab.strings[match_id]
            if label == "DATASET_LABEL":
                span = doc[start:end]
                # 取标签词之后的名词
                nouns = [t for t in span if t.pos_ in ("PROPN", "NOUN") and t.lemma_ not in (
                    "dataset", "corpus", "benchmark", "data",
                )]
                if nouns:
                    ds = " ".join(t.text for t in nouns)
                    if len(ds) > 1:
                        results.append(ds)

        return _dedup(results)[:10]

    def _extract_findings(self, doc: Doc) -> list[str]:
        results = []
        matches = self._matcher(doc)

        for match_id, start, end in matches:
            label = self._nlp.vocab.strings[match_id]
            if label == "FINDING_THAT":
                # 抽取 "that" 后面到句号之间的文本
                that_token = doc[end - 1]  # "that" token
                sent = that_token.sent
                # 从 "that" 之后到句子结尾
                finding_start = that_token.i + 1
                finding_end = sent.end
                if finding_end > finding_start:
                    finding = doc[finding_start:finding_end].text.strip().rstrip(".")
                    if 10 < len(finding) < 300:
                        results.append(finding)

            elif label == "FINDING_SIGNIFICANT":
                # 抽取包含该匹配的整个句子
                token = doc[start]
                sent_text = token.sent.text.strip()
                if 15 < len(sent_text) < 400:
                    results.append(sent_text)

        return _dedup(results)[:5]

    def extract_batch(
        self, documents: list[Document], verbose: bool = True
    ) -> list[AcademicPaperEvent]:
        """批量抽取，利用 spaCy pipe 加速。"""
        self._ensure_loaded()
        results = []
        total = len(documents)

        texts = [d.full_text or "" for d in documents]
        max_chars = self._nlp.max_length

        for i, (doc, spacy_doc) in enumerate(
            zip(documents, self._nlp.pipe(
                [t[:max_chars] if len(t) > max_chars else t for t in texts],
                batch_size=50,
            ))
        ):
            methods = self._extract_methods(spacy_doc)
            datasets = self._extract_datasets(spacy_doc)
            findings = self._extract_findings(spacy_doc)

            event = AcademicPaperEvent(
                doc_id=doc.doc_id,
                title=doc.title,
                doi=doc.doi,
                methods=methods,
                datasets=datasets,
                findings=findings,
                extraction_method=self.name,
            )
            results.append(event)

            if verbose and (i + 1) % 500 == 0:
                print(f"  [{self.name}] 已处理 {i + 1}/{total}")

        if verbose:
            print(f"  [{self.name}] 完成，共 {total} 篇")
        return results
