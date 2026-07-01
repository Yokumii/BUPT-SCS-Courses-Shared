"""
事件模式定义：AcademicPaperEvent 数据类及相关结构。

定义学术论文事件的 7 个信息点：
  1. methods — 研究方法/算法
  2. datasets — 数据集名称
  3. metrics — 评价指标及实验结果
  4. domain_keywords — 研究领域关键词
  5. affiliations — 机构/作者单位
  6. findings — 因果发现/结论
  7. study_characteristics — 样本量、时间范围等研究特征
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class MetricResult:
    """单个评价指标结果。"""
    name: str           # 指标名称, 如 "accuracy"
    value: str          # 数值, 如 "95.3%"
    context: str = ""   # 上下文句子

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value, "context": self.context}

    @classmethod
    def from_dict(cls, d: dict) -> "MetricResult":
        return cls(name=d["name"], value=d["value"], context=d.get("context", ""))


@dataclass
class AcademicPaperEvent:
    """
    学术论文事件 — 7 个信息点组合。

    每篇论文对应一个事件实例，部分字段可为空。
    """
    doc_id: int
    title: str
    doi: str = ""

    # 7 个信息点
    methods: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)
    metrics: list[MetricResult] = field(default_factory=list)
    domain_keywords: list[str] = field(default_factory=list)
    affiliations: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    study_characteristics: dict = field(default_factory=dict)

    # 元信息
    extraction_method: str = ""
    confidence: float = 0.0

    @property
    def field_names(self) -> list[str]:
        """返回 7 个信息点字段名列表。"""
        return [
            "methods", "datasets", "metrics", "domain_keywords",
            "affiliations", "findings", "study_characteristics",
        ]

    @property
    def non_empty_fields(self) -> int:
        """非空字段数量。"""
        count = 0
        for name in self.field_names:
            val = getattr(self, name)
            if val:
                count += 1
        return count

    def to_dict(self) -> dict:
        """序列化为字典（JSON 兼容）。"""
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "doi": self.doi,
            "methods": self.methods,
            "datasets": self.datasets,
            "metrics": [m.to_dict() for m in self.metrics],
            "domain_keywords": self.domain_keywords,
            "affiliations": self.affiliations,
            "findings": self.findings,
            "study_characteristics": self.study_characteristics,
            "extraction_method": self.extraction_method,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AcademicPaperEvent":
        """从字典反序列化。"""
        metrics = [MetricResult.from_dict(m) for m in d.get("metrics", [])]
        return cls(
            doc_id=d["doc_id"],
            title=d["title"],
            doi=d.get("doi", ""),
            methods=d.get("methods", []),
            datasets=d.get("datasets", []),
            metrics=metrics,
            domain_keywords=d.get("domain_keywords", []),
            affiliations=d.get("affiliations", []),
            findings=d.get("findings", []),
            study_characteristics=d.get("study_characteristics", {}),
            extraction_method=d.get("extraction_method", ""),
            confidence=d.get("confidence", 0.0),
        )

    def merge(self, other: "AcademicPaperEvent") -> "AcademicPaperEvent":
        """
        合并另一个事件的抽取结果（去重），用于集成多方法。

        返回新实例，不修改 self 或 other。
        """
        def _merge_lists(a: list, b: list) -> list:
            seen = set()
            result = []
            for item in a + b:
                key = item.lower() if isinstance(item, str) else str(item)
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result

        def _merge_metrics(a: list[MetricResult], b: list[MetricResult]) -> list[MetricResult]:
            seen = set()
            result = []
            for m in a + b:
                key = (m.name.lower(), m.value)
                if key not in seen:
                    seen.add(key)
                    result.append(m)
            return result

        merged_chars = dict(self.study_characteristics)
        merged_chars.update(other.study_characteristics)

        return AcademicPaperEvent(
            doc_id=self.doc_id,
            title=self.title,
            doi=self.doi or other.doi,
            methods=_merge_lists(self.methods, other.methods),
            datasets=_merge_lists(self.datasets, other.datasets),
            metrics=_merge_metrics(self.metrics, other.metrics),
            domain_keywords=_merge_lists(self.domain_keywords, other.domain_keywords),
            affiliations=_merge_lists(self.affiliations, other.affiliations),
            findings=_merge_lists(self.findings, other.findings),
            study_characteristics=merged_chars,
            extraction_method=f"{self.extraction_method}+{other.extraction_method}",
            confidence=max(self.confidence, other.confidence),
        )


def save_events(events: list[AcademicPaperEvent], path: str):
    """批量保存事件到 JSON 文件。"""
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = [e.to_dict() for e in events]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_events(path: str) -> list[AcademicPaperEvent]:
    """从 JSON 文件加载事件。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [AcademicPaperEvent.from_dict(d) for d in data]
