"""
正则表达式抽取器 (L1 baseline)：
使用预定义正则模式匹配学术论文中的结构化信息。

这是课程要求必须实现的 baseline 方法。
"""

import re
from src.parser import Document
from src.base_extractor import BaseExtractor
from src.schema import AcademicPaperEvent, MetricResult


# ──────────────────────────────────────────────
# 正则模式定义
# ──────────────────────────────────────────────

# 评价指标及数值结果
METRIC_PATTERNS = [
    # "accuracy of 95.3%" / "accuracy = 0.95"
    re.compile(
        r'(?P<metric>accuracy|precision|recall|f1(?:-?score)?|auc(?:-roc)?|bleu|rouge|'
        r'perplexity|rmse|mae|mse|r[²2]|specificity|sensitivity|mape|'
        r'map|ndcg|mrr|hit.?rate|top-?\d+\s*accuracy)'
        r'\s*(?:of|=|:|is|was|reached|achieved)?\s*'
        r'(?P<value>\d+\.?\d*)\s*%?',
        re.IGNORECASE,
    ),
    # "p < 0.05" / "p = 0.001" / "p-value < .01"
    re.compile(
        r'(?P<metric>p(?:-?value)?)\s*(?P<value>[<>=≤≥]+\s*\.?\d+\.?\d*)',
        re.IGNORECASE,
    ),
    # "AUC of 0.89" / "F1 score of 0.92"
    re.compile(
        r'(?P<metric>[A-Z][A-Za-z0-9-]*(?:\s+score)?)\s+of\s+(?P<value>\d+\.?\d*%?)',
    ),
    # "achieved 95.3% accuracy"
    re.compile(
        r'(?:achieved?|obtained?|reached?|reported?)\s+'
        r'(?:an?\s+)?(?P<value>\d+\.?\d*\s*%)\s+'
        r'(?P<metric>accuracy|precision|recall|f1(?:-?score)?)',
        re.IGNORECASE,
    ),
]

# 样本量
SAMPLE_PATTERNS = [
    # "N = 1,234" / "n=500"
    re.compile(r'[Nn]\s*=\s*(?P<n>[\d,]+)'),
    # "1,234 participants" / "500 subjects"
    re.compile(
        r'(?P<n>[\d,]+)\s+'
        r'(?:participants|subjects|patients|samples|respondents|observations|'
        r'individuals|cases|students|adults|children|firms|companies|countries)',
        re.IGNORECASE,
    ),
    # "sample of 500"
    re.compile(r'sample\s+(?:of|size)\s+(?P<n>[\d,]+)', re.IGNORECASE),
]

# 数据集名称
DATASET_PATTERNS = [
    # 常见数据集名称（大写开头或全大写缩写）
    re.compile(
        r'\b(?P<ds>MNIST|CIFAR-?(?:10|100)|ImageNet|COCO|SQuAD|GLUE|SuperGLUE|'
        r'WMT-?\d+|Penn\s*Treebank|PTB|SST-?\d*|IMDB|Yelp|Amazon\s*Reviews?|'
        r'SNLI|MultiNLI|CoNLL-?\d+|ACE-?\d+|OntoNotes|WikiText|'
        r'MS\s*MARCO|TREC|Reuters|20\s*Newsgroups|UCI\b[^.]*)'
    ),
    # "dataset: [NAME]" / "dataset called [NAME]"
    re.compile(
        r'(?:dataset|corpus|benchmark)\s*(?:called|named|:)\s*'
        r'(?:the\s+)?(?P<ds>[A-Z][\w-]+(?:\s+[\w-]+){0,3})',
        re.IGNORECASE,
    ),
    # "trained on [NAME]" / "evaluated on [NAME]"
    re.compile(
        r'(?:trained|evaluated|tested|fine-?tuned)\s+on\s+'
        r'(?:the\s+)?(?P<ds>[A-Z][\w-]+(?:\s+[\w-]+){0,2})',
    ),
]

# 研究方法
METHOD_PATTERNS = [
    # "using [method]" / "we use [method]"
    re.compile(
        r'(?:using|use|employ(?:ing)?|apply(?:ing)?|adopt(?:ing)?|implement(?:ing)?)\s+'
        r'(?:a\s+|an\s+|the\s+)?'
        r'(?P<method>[A-Z][\w-]*(?:\s+[\w-]+){0,4})',
    ),
    # "we propose [method]" / "we introduce [method]"
    re.compile(
        r'(?:propos(?:e|ing)|introduc(?:e|ing)|develop(?:ing)?|present(?:ing)?)\s+'
        r'(?:a\s+|an\s+|the\s+)?'
        r'(?:novel\s+|new\s+)?'
        r'(?P<method>[A-Z][\w-]*(?:\s+[\w-]+){0,4})',
    ),
    # 常见方法名关键词
    re.compile(
        r'\b(?P<method>(?:linear|logistic|ridge|lasso)\s+regression|'
        r'random\s+forest|gradient\s+boost(?:ing)?|'
        r'(?:deep|convolutional|recurrent)\s+(?:neural\s+)?network|'
        r'support\s+vector\s+machine|SVM|'
        r'transformer|BERT|GPT|LSTM|GRU|CNN|RNN|GAN|VAE|'
        r'k-?means|PCA|t-?SNE|UMAP|'
        r'(?:difference-?in-?differences?|DID|'
        r'regression\s+discontinuity|instrumental\s+variables?|IV|'
        r'propensity\s+score|OLS|2SLS|GMM|'
        r'fixed\s+effects?|random\s+effects?))\b',
        re.IGNORECASE,
    ),
]

# 年份范围
YEAR_RANGE_PATTERNS = [
    # "from 2010 to 2020" / "between 2010 and 2020"
    re.compile(
        r'(?:from|between)\s+(?P<start>\d{4})\s+(?:to|and)\s+(?P<end>\d{4})',
        re.IGNORECASE,
    ),
    # "2010-2020" / "2010–2020"
    re.compile(r'(?P<start>\d{4})\s*[-–]\s*(?P<end>\d{4})'),
    # "during 2010-2020"
    re.compile(
        r'(?:during|over|spanning)\s+(?:the\s+)?(?:period\s+)?'
        r'(?P<start>\d{4})\s*[-–]\s*(?P<end>\d{4})',
        re.IGNORECASE,
    ),
]

# 因果/结论
FINDING_PATTERNS = [
    # "we find that ..." / "results show that ..."
    re.compile(
        r'(?:we\s+)?(?:find|show|demonstrate|observe|discover|reveal|confirm|conclude|'
        r'suggest|indicate|provide\s+evidence)\s+that\s+'
        r'(?P<finding>[^.]{10,200})\.',
        re.IGNORECASE,
    ),
    # "X significantly increases/decreases Y"
    re.compile(
        r'(?P<finding>[\w\s]{5,60}\s+'
        r'(?:significantly|positively|negatively|strongly|marginally)\s+'
        r'(?:increase[sd]?|decrease[sd]?|affect[sd]?|improve[sd]?|reduce[sd]?|'
        r'enhance[sd]?|correlate[sd]?\s+with|predict[sd]?|influence[sd]?)'
        r'[\w\s]{5,100})\.',
        re.IGNORECASE,
    ),
]

# 机构
AFFILIATION_PATTERNS = [
    # "University of XXX" / "XXX University"
    re.compile(
        r'(?P<aff>(?:University|Institute|College|School|Laboratory|Lab|Department|Center|Centre)'
        r'\s+of\s+[A-Z][\w\s,]+?(?=\.|,|\n|;|$))',
    ),
    re.compile(
        r'(?P<aff>[A-Z][\w]+(?:\s+[A-Z][\w]+)*\s+'
        r'(?:University|Institute|College|Laboratory|Lab|Hospital|School))\b',
    ),
    # 缩写机构名
    re.compile(
        r'\b(?P<aff>MIT|Stanford|Harvard|Oxford|Cambridge|Caltech|Berkeley|'
        r'Princeton|Yale|Columbia|Cornell|Penn|CMU|NYU|UCLA|USC|ETH|EPFL|'
        r'INRIA|Max\s+Planck|Microsoft\s+Research|Google\s+(?:Research|Brain|DeepMind)|'
        r'Meta\s+AI|OpenAI|Allen\s+AI|IBM\s+Research)\b',
    ),
]


def _clean(text: str) -> str:
    """去除首尾空白及多余空格。"""
    return re.sub(r'\s+', ' ', text).strip()


def _dedup(items: list[str]) -> list[str]:
    """保序去重。"""
    seen = set()
    result = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


class RegexExtractor(BaseExtractor):
    """正则表达式抽取器 (L1 baseline)。"""

    @property
    def name(self) -> str:
        return "regex"

    def extract(self, doc: Document) -> AcademicPaperEvent:
        text = doc.full_text
        if not text:
            return AcademicPaperEvent(
                doc_id=doc.doc_id, title=doc.title, doi=doc.doi, extraction_method=self.name
            )

        methods = self._extract_methods(text)
        datasets = self._extract_datasets(text)
        metrics = self._extract_metrics(text)
        domain_kw = self._extract_domain_keywords(text, doc.title, doc.journal)
        affiliations = self._extract_affiliations(text, doc.authors)
        findings = self._extract_findings(text)
        study_chars = self._extract_study_characteristics(text)

        return AcademicPaperEvent(
            doc_id=doc.doc_id,
            title=doc.title,
            doi=doc.doi,
            methods=methods,
            datasets=datasets,
            metrics=metrics,
            domain_keywords=domain_kw,
            affiliations=affiliations,
            findings=findings,
            study_characteristics=study_chars,
            extraction_method=self.name,
        )

    # ── 子抽取函数 ──────────────────────────────

    def _extract_methods(self, text: str) -> list[str]:
        results = []
        for pat in METHOD_PATTERNS:
            for m in pat.finditer(text):
                method = _clean(m.group("method"))
                if len(method) > 2:
                    results.append(method)
        return _dedup(results)[:15]

    def _extract_datasets(self, text: str) -> list[str]:
        results = []
        for pat in DATASET_PATTERNS:
            for m in pat.finditer(text):
                ds = _clean(m.group("ds"))
                if len(ds) > 1:
                    results.append(ds)
        return _dedup(results)[:10]

    def _extract_metrics(self, text: str) -> list[MetricResult]:
        results = []
        seen = set()
        for pat in METRIC_PATTERNS:
            for m in pat.finditer(text):
                metric_name = _clean(m.group("metric")).lower()
                value = _clean(m.group("value"))
                key = (metric_name, value)
                if key not in seen:
                    seen.add(key)
                    # 提取上下文：匹配位置前后各 100 字符
                    start = max(0, m.start() - 50)
                    end = min(len(text), m.end() + 50)
                    context = text[start:end].replace("\n", " ").strip()
                    results.append(MetricResult(
                        name=metric_name, value=value, context=context
                    ))
        return results[:20]

    def _extract_domain_keywords(
        self, text: str, title: str, journal: str
    ) -> list[str]:
        """从标题和期刊名中提取领域关键词。"""
        keywords = []
        # 从标题提取：取较长的名词短语
        title_words = re.findall(r'\b[a-z]{3,}(?:\s+[a-z]{3,})*\b', title.lower())
        keywords.extend(title_words[:5])
        # 期刊名常包含领域信息
        if journal:
            keywords.append(journal)
        return _dedup(keywords)[:10]

    def _extract_affiliations(self, text: str, authors_field: str) -> list[str]:
        results = []
        # 先从作者字段提取
        search_text = f"{authors_field}\n{text[:3000]}"
        for pat in AFFILIATION_PATTERNS:
            for m in pat.finditer(search_text):
                aff = _clean(m.group("aff"))
                if len(aff) > 2:
                    results.append(aff)
        return _dedup(results)[:10]

    def _extract_findings(self, text: str) -> list[str]:
        results = []
        # 聚焦摘要和结论部分
        for pat in FINDING_PATTERNS:
            for m in pat.finditer(text):
                finding = _clean(m.group("finding"))
                if 10 < len(finding) < 300:
                    results.append(finding)
        return _dedup(results)[:5]

    def _extract_study_characteristics(self, text: str) -> dict:
        chars: dict = {}

        # 样本量
        for pat in SAMPLE_PATTERNS:
            m = pat.search(text)
            if m:
                n = m.group("n").replace(",", "")
                if n.isdigit() and int(n) > 1:
                    chars["sample_size"] = int(n)
                    break

        # 时间范围
        for pat in YEAR_RANGE_PATTERNS:
            m = pat.search(text)
            if m:
                start, end = m.group("start"), m.group("end")
                s, e = int(start), int(end)
                if 1900 <= s <= 2030 and 1900 <= e <= 2030 and s < e:
                    chars["time_range"] = f"{start}-{end}"
                    break

        return chars
