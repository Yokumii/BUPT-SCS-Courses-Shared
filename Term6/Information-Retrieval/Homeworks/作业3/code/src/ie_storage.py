"""
IE 结果存储：使用 SQLite 保存抽取结果与方法级统计，
支持分页、搜索和流式迭代，避免 Web 端全量加载 JSON。
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from src.schema import AcademicPaperEvent


@dataclass
class MethodSummary:
    """单个抽取方法的统计摘要。"""

    method: str
    total_docs: int
    has_methods: int
    has_datasets: int
    has_metrics: int
    has_affiliations: int
    has_findings: int
    has_domain_keywords: int
    has_study_characteristics: int
    avg_fields: float

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "total_docs": self.total_docs,
            "has_methods": self.has_methods,
            "has_datasets": self.has_datasets,
            "has_metrics": self.has_metrics,
            "has_affiliations": self.has_affiliations,
            "has_findings": self.has_findings,
            "has_domain_keywords": self.has_domain_keywords,
            "has_study_characteristics": self.has_study_characteristics,
            "avg_fields": self.avg_fields,
        }


class MethodEventWriter:
    """方法结果写入器，支持分批追加并在结束时落库统计。"""

    def __init__(self, conn: sqlite3.Connection, method: str, autocommit: bool = True):
        self._conn = conn
        self._method = method
        self._autocommit = autocommit
        self._closed = False
        self._summary = {
            "total_docs": 0,
            "has_methods": 0,
            "has_datasets": 0,
            "has_metrics": 0,
            "has_affiliations": 0,
            "has_findings": 0,
            "has_domain_keywords": 0,
            "has_study_characteristics": 0,
            "fields_sum": 0,
        }

        self._conn.execute("DELETE FROM method_events WHERE method = ?", (method,))
        self._conn.execute("DELETE FROM method_summaries WHERE method = ?", (method,))

    def append(self, events: Iterable[AcademicPaperEvent]):
        """追加一批事件。"""
        rows = []
        for event in events:
            self._summary["total_docs"] += 1
            self._summary["fields_sum"] += event.non_empty_fields
            self._summary["has_methods"] += int(bool(event.methods))
            self._summary["has_datasets"] += int(bool(event.datasets))
            self._summary["has_metrics"] += int(bool(event.metrics))
            self._summary["has_affiliations"] += int(bool(event.affiliations))
            self._summary["has_findings"] += int(bool(event.findings))
            self._summary["has_domain_keywords"] += int(bool(event.domain_keywords))
            self._summary["has_study_characteristics"] += int(bool(event.study_characteristics))
            rows.append(
                (
                    self._method,
                    event.doc_id,
                    event.title,
                    json.dumps(event.to_dict(), ensure_ascii=False),
                )
            )

        if rows:
            self._conn.executemany(
                """
                INSERT INTO method_events (method, doc_id, title, payload_json)
                VALUES (?, ?, ?, ?)
                """,
                rows,
            )

    def finish(self) -> MethodSummary:
        """完成写入并保存方法摘要。"""
        if self._closed:
            raise RuntimeError("writer already closed")

        total_docs = self._summary["total_docs"]
        avg_fields = self._summary["fields_sum"] / total_docs if total_docs else 0.0

        summary = MethodSummary(
            method=self._method,
            total_docs=total_docs,
            has_methods=self._summary["has_methods"],
            has_datasets=self._summary["has_datasets"],
            has_metrics=self._summary["has_metrics"],
            has_affiliations=self._summary["has_affiliations"],
            has_findings=self._summary["has_findings"],
            has_domain_keywords=self._summary["has_domain_keywords"],
            has_study_characteristics=self._summary["has_study_characteristics"],
            avg_fields=avg_fields,
        )

        self._conn.execute(
            """
            INSERT INTO method_summaries (
                method, total_docs, has_methods, has_datasets, has_metrics,
                has_affiliations, has_findings, has_domain_keywords,
                has_study_characteristics, avg_fields
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                summary.method,
                summary.total_docs,
                summary.has_methods,
                summary.has_datasets,
                summary.has_metrics,
                summary.has_affiliations,
                summary.has_findings,
                summary.has_domain_keywords,
                summary.has_study_characteristics,
                summary.avg_fields,
            ),
        )
        if self._autocommit:
            self._conn.commit()
        self._closed = True
        return summary


class IEStorage:
    """SQLite 后端的 IE 结果存储。"""

    def __init__(self, base_path: str | os.PathLike = "index/ie"):
        path = Path(base_path)
        self.base_dir = path if path.suffix != ".db" else path.parent
        self.db_path = path if path.suffix == ".db" else path / "events.db"
        os.makedirs(self.base_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS method_events (
                method TEXT NOT NULL,
                doc_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (method, doc_id)
            );

            CREATE TABLE IF NOT EXISTS method_summaries (
                method TEXT PRIMARY KEY,
                total_docs INTEGER NOT NULL,
                has_methods INTEGER NOT NULL,
                has_datasets INTEGER NOT NULL,
                has_metrics INTEGER NOT NULL,
                has_affiliations INTEGER NOT NULL,
                has_findings INTEGER NOT NULL,
                has_domain_keywords INTEGER NOT NULL,
                has_study_characteristics INTEGER NOT NULL,
                avg_fields REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_method_events_lookup
            ON method_events (method, doc_id);
            """
        )
        self.conn.commit()

    def open_writer(self, method: str, autocommit: bool = True) -> MethodEventWriter:
        """开启某个方法的分批写入。"""
        return MethodEventWriter(self.conn, method, autocommit=autocommit)

    def has_method(self, method: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM method_summaries WHERE method = ?",
            (method,),
        ).fetchone()
        return row is not None

    def list_method_summaries(self) -> dict[str, dict]:
        """返回所有方法的轻量统计。"""
        rows = self.conn.execute(
            """
            SELECT method, total_docs, has_methods, has_datasets, has_metrics,
                   has_affiliations, has_findings, has_domain_keywords,
                   has_study_characteristics, avg_fields
            FROM method_summaries
            ORDER BY method
            """
        ).fetchall()
        return {
            row["method"]: MethodSummary(
                method=row["method"],
                total_docs=row["total_docs"],
                has_methods=row["has_methods"],
                has_datasets=row["has_datasets"],
                has_metrics=row["has_metrics"],
                has_affiliations=row["has_affiliations"],
                has_findings=row["has_findings"],
                has_domain_keywords=row["has_domain_keywords"],
                has_study_characteristics=row["has_study_characteristics"],
                avg_fields=row["avg_fields"],
            ).to_dict()
            for row in rows
        }

    def fetch_events_page(
        self, method: str, offset: int, limit: int, search: str = ""
    ) -> tuple[list[AcademicPaperEvent], int]:
        """分页读取事件，并返回匹配总数。"""
        params: list = [method]
        where_sql = "WHERE method = ?"

        if search:
            search_like = f"%{search.lower()}%"
            where_sql += " AND (LOWER(title) LIKE ? OR LOWER(payload_json) LIKE ?)"
            params.extend([search_like, search_like])

        count_row = self.conn.execute(
            f"SELECT COUNT(*) AS cnt FROM method_events {where_sql}",
            params,
        ).fetchone()
        total = int(count_row["cnt"]) if count_row else 0

        rows = self.conn.execute(
            f"""
            SELECT payload_json
            FROM method_events
            {where_sql}
            ORDER BY doc_id
            LIMIT ? OFFSET ?
            """,
            [*params, limit, offset],
        ).fetchall()

        events = [
            AcademicPaperEvent.from_dict(json.loads(row["payload_json"]))
            for row in rows
        ]
        return events, total

    def get_event(self, method: str, doc_id: int) -> AcademicPaperEvent | None:
        """按方法和文档 ID 查询单条事件。"""
        row = self.conn.execute(
            """
            SELECT payload_json
            FROM method_events
            WHERE method = ? AND doc_id = ?
            """,
            (method, doc_id),
        ).fetchone()
        if row is None:
            return None
        return AcademicPaperEvent.from_dict(json.loads(row["payload_json"]))

    def iter_events(self, method: str) -> Iterator[AcademicPaperEvent]:
        """按 doc_id 顺序流式读取方法事件。"""
        cursor = self.conn.execute(
            """
            SELECT payload_json
            FROM method_events
            WHERE method = ?
            ORDER BY doc_id
            """,
            (method,),
        )
        for row in cursor:
            yield AcademicPaperEvent.from_dict(json.loads(row["payload_json"]))
