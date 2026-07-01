"""
LLM 零样本抽取器 (L4)：
通过 OpenAI 兼容 API（如 GPT-4o-mini）从论文中进行结构化信息抽取。

仅对评估子集使用（50-100 篇），不做全量处理。
"""

import json
import os

from openai import OpenAI

from src.parser import Document
from src.base_extractor import BaseExtractor
from src.schema import AcademicPaperEvent, MetricResult


EXTRACTION_PROMPT = """\
You are an academic paper information extraction system.
Extract the following fields from the given paper text and return a JSON object.

Fields:
- methods: list of research methods/algorithms used (strings)
- datasets: list of dataset names mentioned (strings)
- metrics: list of objects with {name, value} for reported evaluation metrics
- domain_keywords: list of research domain/topic keywords (strings)
- affiliations: list of author institutions/organizations (strings)
- findings: list of key findings or conclusions (strings, each < 200 chars)
- study_characteristics: object with optional keys: sample_size (int), time_range (string like "2010-2020"), regions (list of strings)

Rules:
- Only extract information explicitly stated in the text
- Return empty lists/objects for fields with no information
- For metrics, include the metric name and its numeric value
- Keep findings concise (< 200 characters each)
- Return valid JSON only, no markdown or explanation

Paper text:
{text}
"""


class LLMExtractor(BaseExtractor):
    """LLM 零样本抽取器 (L4)。"""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        max_input_chars: int = 8000,
    ):
        self._base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._model = model
        self._max_input_chars = max_input_chars
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            self._client = OpenAI(base_url=self._base_url, api_key=self._api_key)

    @property
    def name(self) -> str:
        return "llm"

    def extract(self, doc: Document) -> AcademicPaperEvent:
        self._ensure_client()

        text = doc.full_text
        if not text:
            return AcademicPaperEvent(
                doc_id=doc.doc_id, title=doc.title, doi=doc.doi, extraction_method=self.name
            )

        # 截断文本控制 token 消耗
        if len(text) > self._max_input_chars:
            text = text[:self._max_input_chars]

        prompt = EXTRACTION_PROMPT.format(text=text)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=2000,
            )
            content = response.choices[0].message.content.strip()
            # 清理可能的 markdown 包裹
            if content.startswith("```"):
                content = content.split("\n", 1)[-1]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            data = json.loads(content)
        except Exception as e:
            print(f"  [llm] doc_id={doc.doc_id} 抽取失败: {e}")
            return AcademicPaperEvent(
                doc_id=doc.doc_id, title=doc.title, doi=doc.doi, extraction_method=self.name
            )

        return self._parse_response(doc, data)

    def _parse_response(self, doc: Document, data: dict) -> AcademicPaperEvent:
        """将 LLM 返回的 JSON 转换为 AcademicPaperEvent。"""
        metrics = []
        for m in data.get("metrics", []):
            if isinstance(m, dict) and "name" in m and "value" in m:
                metrics.append(MetricResult(
                    name=str(m["name"]),
                    value=str(m["value"]),
                    context=str(m.get("context", "")),
                ))

        study_chars = data.get("study_characteristics", {})
        if not isinstance(study_chars, dict):
            study_chars = {}

        return AcademicPaperEvent(
            doc_id=doc.doc_id,
            title=doc.title,
            doi=doc.doi,
            methods=[str(m) for m in data.get("methods", []) if m],
            datasets=[str(d) for d in data.get("datasets", []) if d],
            metrics=metrics,
            domain_keywords=[str(k) for k in data.get("domain_keywords", []) if k],
            affiliations=[str(a) for a in data.get("affiliations", []) if a],
            findings=[str(f) for f in data.get("findings", []) if f],
            study_characteristics=study_chars,
            extraction_method=self.name,
            confidence=0.9,
        )
