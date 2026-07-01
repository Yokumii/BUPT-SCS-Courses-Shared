"""
集成器：合并多种抽取方法的结果，通过投票/融合/级联策略提升精度。
"""

from src.parser import Document
from src.base_extractor import BaseExtractor
from src.schema import AcademicPaperEvent, MetricResult


class EnsembleExtractor(BaseExtractor):
    """多方法集成抽取器。"""

    def __init__(
        self,
        extractors: list[BaseExtractor],
        strategy: str = "merge",
        min_votes: int = 1,
    ):
        """
        Args:
            extractors: 参与集成的抽取器列表
            strategy: 集成策略
                - "merge": 合并所有结果并去重（默认）
                - "vote": 仅保留被 ≥ min_votes 种方法抽取的信息
            min_votes: vote 策略下的最小投票数
        """
        self._extractors = extractors
        self._strategy = strategy
        self._min_votes = min_votes

    @property
    def name(self) -> str:
        names = "+".join(e.name for e in self._extractors)
        return f"ensemble({names})"

    def extract(self, doc: Document) -> AcademicPaperEvent:
        events = [ext.extract(doc) for ext in self._extractors]

        if self._strategy == "vote":
            return self._vote_merge(doc, events)
        else:
            return self._simple_merge(doc, events)

    def extract_batch(
        self, documents: list[Document], verbose: bool = True
    ) -> list[AcademicPaperEvent]:
        """批量集成：先让各抽取器分别批量处理，再逐文档合并。"""
        # 各抽取器分别批量抽取
        all_results: list[list[AcademicPaperEvent]] = []
        for ext in self._extractors:
            if verbose:
                print(f"  [集成] 运行 {ext.name}...")
            batch = ext.extract_batch(documents, verbose=verbose)
            all_results.append(batch)

        # 逐文档合并
        merged = []
        for i, doc in enumerate(documents):
            events = [results[i] for results in all_results]
            if self._strategy == "vote":
                m = self._vote_merge(doc, events)
            else:
                m = self._simple_merge(doc, events)
            merged.append(m)

        if verbose:
            print(f"  [集成] 完成，共 {len(documents)} 篇")
        return merged

    def _simple_merge(
        self, doc: Document, events: list[AcademicPaperEvent]
    ) -> AcademicPaperEvent:
        """简单合并：将所有事件结果去重合并。"""
        if not events:
            return AcademicPaperEvent(
                doc_id=doc.doc_id, title=doc.title, doi=doc.doi, extraction_method=self.name
            )

        result = events[0]
        for event in events[1:]:
            result = result.merge(event)
        result.extraction_method = self.name
        return result

    def _vote_merge(
        self, doc: Document, events: list[AcademicPaperEvent]
    ) -> AcademicPaperEvent:
        """投票合并：仅保留被多种方法提取的信息。"""
        threshold = self._min_votes

        def _vote_strings(field_name: str) -> list[str]:
            counter: dict[str, int] = {}
            original: dict[str, str] = {}
            for event in events:
                val = getattr(event, field_name, [])
                if isinstance(val, list):
                    for item in val:
                        key = item.lower().strip()
                        counter[key] = counter.get(key, 0) + 1
                        original[key] = item
            return [original[k] for k, v in counter.items() if v >= threshold]

        def _vote_metrics() -> list[MetricResult]:
            counter: dict[tuple, int] = {}
            original: dict[tuple, MetricResult] = {}
            for event in events:
                for m in event.metrics:
                    key = (m.name.lower(), m.value)
                    counter[key] = counter.get(key, 0) + 1
                    original[key] = m
            return [original[k] for k, v in counter.items() if v >= threshold]

        # 合并 study_characteristics（非投票，直接合并）
        merged_chars = {}
        for event in events:
            merged_chars.update(event.study_characteristics)

        return AcademicPaperEvent(
            doc_id=doc.doc_id,
            title=doc.title,
            doi=doc.doi,
            methods=_vote_strings("methods"),
            datasets=_vote_strings("datasets"),
            metrics=_vote_metrics(),
            domain_keywords=_vote_strings("domain_keywords"),
            affiliations=_vote_strings("affiliations"),
            findings=_vote_strings("findings"),
            study_characteristics=merged_chars,
            extraction_method=self.name,
        )
