"""
抽取器基类：定义所有 IE 抽取器的统一接口。
"""

from abc import ABC, abstractmethod

from src.parser import Document
from src.schema import AcademicPaperEvent


class BaseExtractor(ABC):
    """所有抽取器的基类。"""

    @abstractmethod
    def extract(self, doc: Document) -> AcademicPaperEvent:
        """
        从单篇文档中抽取事件信息。

        Args:
            doc: V1 解析的 Document 对象（含 title, abstract, body 等字段）

        Returns:
            AcademicPaperEvent 实例
        """
        ...

    def extract_batch(
        self, documents: list[Document], verbose: bool = True
    ) -> list[AcademicPaperEvent]:
        """批量抽取，带进度提示。"""
        results = []
        total = len(documents)
        for i, doc in enumerate(documents):
            results.append(self.extract(doc))
            if verbose and (i + 1) % 500 == 0:
                print(f"  [{self.name}] 已处理 {i + 1}/{total}")
        if verbose:
            print(f"  [{self.name}] 完成，共 {total} 篇")
        return results

    @property
    @abstractmethod
    def name(self) -> str:
        """抽取器名称标识。"""
        ...
