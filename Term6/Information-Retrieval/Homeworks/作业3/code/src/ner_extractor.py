"""
NER 抽取器 (L3)：
使用 spaCy / SciSpaCy 预训练 NER 模型识别学术论文中的命名实体，
并将实体类型映射到 IE 事件字段。
"""

from collections import defaultdict

from src.parser import Document
from src.base_extractor import BaseExtractor
from src.schema import AcademicPaperEvent, MetricResult
from src.nlp_pipeline import get_nlp


# spaCy 实体类型 → IE 字段映射
ENTITY_FIELD_MAP = {
    "ORG": "affiliations",
    "GPE": "study_characteristics",    # 地域信息
    "DATE": "study_characteristics",   # 日期信息
    "CARDINAL": "study_characteristics",  # 数字（样本量等）
    "PERCENT": "metrics",
    "PERSON": None,  # 暂不使用
    "MONEY": None,
    "QUANTITY": None,
}

# 机构关键词过滤：仅保留包含这些词的 ORG 实体
ACADEMIC_ORG_KEYWORDS = {
    "university", "institute", "college", "school", "laboratory", "lab",
    "department", "center", "centre", "hospital", "academy",
    "research", "science", "technology",
}

# 非机构名过滤（常被误识别为 ORG 的词）
ORG_BLACKLIST = {
    "ieee", "acm", "springer", "elsevier", "wiley", "nature",
    "plos", "bmc", "mdpi", "frontiers", "arxiv",
    "table", "figure", "section", "chapter", "appendix",
    "eq", "equation", "method", "model", "algorithm",
}


def _dedup(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


class NERExtractor(BaseExtractor):
    """NER 预训练模型抽取器 (L3)。"""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._model_name = model_name
        self._nlp = None

    def _ensure_loaded(self):
        if self._nlp is None:
            self._nlp = get_nlp(self._model_name)

    @property
    def name(self) -> str:
        return "ner"

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

        # 按实体类型收集
        entity_groups: dict[str, list] = defaultdict(list)
        for ent in spacy_doc.ents:
            entity_groups[ent.label_].append(ent.text.strip())

        # 映射到 IE 字段
        affiliations = self._filter_affiliations(entity_groups.get("ORG", []))
        metrics = self._extract_metrics_from_entities(entity_groups.get("PERCENT", []), text)
        domain_keywords = self._extract_domain_keywords(spacy_doc, doc.title)
        study_chars = self._extract_study_chars(entity_groups)

        return AcademicPaperEvent(
            doc_id=doc.doc_id,
            title=doc.title,
            doi=doc.doi,
            affiliations=affiliations,
            metrics=metrics,
            domain_keywords=domain_keywords,
            study_characteristics=study_chars,
            extraction_method=self.name,
        )

    def _filter_affiliations(self, orgs: list[str]) -> list[str]:
        """过滤 ORG 实体，仅保留学术机构。"""
        results = []
        for org in orgs:
            lower = org.lower()
            # 跳过黑名单
            if lower in ORG_BLACKLIST:
                continue
            # 过滤过短的
            if len(org) < 3:
                continue
            # 优先保留包含机构关键词的
            if any(kw in lower for kw in ACADEMIC_ORG_KEYWORDS):
                results.append(org)
            # 也保留全大写缩写（可能是机构缩写如 MIT、CMU）
            elif org.isupper() and 2 <= len(org) <= 10:
                results.append(org)
        return _dedup(results)[:10]

    def _extract_metrics_from_entities(
        self, percents: list[str], text: str
    ) -> list[MetricResult]:
        """从 PERCENT 实体中提取指标。"""
        results = []
        for pct in percents:
            # 查找此百分比在文本中的上下文
            idx = text.find(pct)
            if idx >= 0:
                start = max(0, idx - 80)
                end = min(len(text), idx + len(pct) + 30)
                context = text[start:end].replace("\n", " ").strip()
                results.append(MetricResult(
                    name="percentage", value=pct, context=context
                ))
        return results[:15]

    def _extract_domain_keywords(self, spacy_doc, title: str) -> list[str]:
        """使用名词短语（noun chunks）提取领域关键词。"""
        keywords = []

        # 从标题提取 noun chunks
        title_doc = self._nlp(title) if title else None
        if title_doc:
            for chunk in title_doc.noun_chunks:
                text = chunk.text.strip()
                if 3 < len(text) < 50:
                    keywords.append(text)

        # 从文档提取高频 noun chunks
        chunk_freq: dict[str, int] = defaultdict(int)
        for chunk in spacy_doc.noun_chunks:
            text = chunk.text.lower().strip()
            if 3 < len(text) < 50:
                chunk_freq[text] += 1

        # 取频率最高的
        sorted_chunks = sorted(chunk_freq.items(), key=lambda x: x[1], reverse=True)
        for text, freq in sorted_chunks[:10]:
            if freq >= 2:
                keywords.append(text)

        return _dedup(keywords)[:10]

    def _extract_study_chars(self, entity_groups: dict) -> dict:
        """从实体中提取研究特征。"""
        chars = {}

        # 地域 (GPE)
        gpes = entity_groups.get("GPE", [])
        if gpes:
            chars["regions"] = _dedup(gpes)[:5]

        # 日期 (DATE) - 找年份
        dates = entity_groups.get("DATE", [])
        years = set()
        for d in dates:
            # 提取 4 位数年份
            import re
            for m in re.finditer(r'\b((?:19|20)\d{2})\b', d):
                years.add(int(m.group(1)))
        if years:
            sorted_years = sorted(years)
            if len(sorted_years) >= 2:
                chars["time_range"] = f"{sorted_years[0]}-{sorted_years[-1]}"

        return chars

    def extract_batch(
        self, documents: list[Document], verbose: bool = True
    ) -> list[AcademicPaperEvent]:
        """批量抽取，利用 spaCy pipe 加速。"""
        self._ensure_loaded()
        results = []
        total = len(documents)
        max_chars = self._nlp.max_length

        texts = []
        for d in documents:
            t = d.full_text or ""
            texts.append(t[:max_chars] if len(t) > max_chars else t)

        for i, (doc, spacy_doc) in enumerate(
            zip(documents, self._nlp.pipe(texts, batch_size=50))
        ):
            # 收集实体
            entity_groups: dict[str, list] = defaultdict(list)
            for ent in spacy_doc.ents:
                entity_groups[ent.label_].append(ent.text.strip())

            text = texts[i]
            affiliations = self._filter_affiliations(entity_groups.get("ORG", []))
            metrics = self._extract_metrics_from_entities(entity_groups.get("PERCENT", []), text)
            domain_keywords = self._extract_domain_keywords(spacy_doc, doc.title)
            study_chars = self._extract_study_chars(entity_groups)

            event = AcademicPaperEvent(
                doc_id=doc.doc_id,
                title=doc.title,
                doi=doc.doi,
                affiliations=affiliations,
                metrics=metrics,
                domain_keywords=domain_keywords,
                study_characteristics=study_chars,
                extraction_method=self.name,
            )
            results.append(event)

            if verbose and (i + 1) % 500 == 0:
                print(f"  [{self.name}] 已处理 {i + 1}/{total}")

        if verbose:
            print(f"  [{self.name}] 完成，共 {total} 篇")
        return results
