"""
测试 IE 结果存储模块。
"""

from src.ie_storage import IEStorage
from src.schema import AcademicPaperEvent, MetricResult


def _make_event(doc_id: int, title: str, method: str, *, methods=None, datasets=None):
    return AcademicPaperEvent(
        doc_id=doc_id,
        title=title,
        methods=methods or [],
        datasets=datasets or [],
        metrics=[MetricResult(name="accuracy", value="95%")] if doc_id == 0 else [],
        findings=["important finding"] if doc_id == 1 else [],
        extraction_method=method,
    )


class TestIEStorage:
    """测试 SQLite 结果存储的分页与统计能力。"""

    def test_write_and_list_method_stats(self, tmp_path):
        storage = IEStorage(tmp_path)
        writer = storage.open_writer("regex")
        writer.append(
            [
                _make_event(0, "Transformer for Healthcare", "regex", methods=["transformer"]),
                _make_event(1, "Climate Policy Dataset Study", "regex", datasets=["PolicyBench"]),
            ]
        )
        writer.finish()

        summaries = storage.list_method_summaries()
        assert list(summaries) == ["regex"]
        assert summaries["regex"]["total_docs"] == 2
        assert summaries["regex"]["has_methods"] == 1
        assert summaries["regex"]["has_datasets"] == 1

    def test_fetch_page_and_search(self, tmp_path):
        storage = IEStorage(tmp_path)
        writer = storage.open_writer("spacy")
        writer.append(
            [
                _make_event(0, "Transformer for Healthcare", "spacy", methods=["transformer"]),
                _make_event(1, "Climate Policy Dataset Study", "spacy", datasets=["PolicyBench"]),
                _make_event(2, "Natural Language Processing", "spacy", methods=["bert"]),
            ]
        )
        writer.finish()

        page, total = storage.fetch_events_page("spacy", offset=1, limit=1)
        assert total == 3
        assert [event.doc_id for event in page] == [1]

        matches, matched_total = storage.fetch_events_page("spacy", offset=0, limit=10, search="policy")
        assert matched_total == 1
        assert matches[0].doc_id == 1

    def test_get_event_and_iter_events(self, tmp_path):
        storage = IEStorage(tmp_path)
        writer = storage.open_writer("ner")
        writer.append(
            [
                _make_event(0, "Transformer for Healthcare", "ner", methods=["transformer"]),
                _make_event(1, "Climate Policy Dataset Study", "ner", datasets=["PolicyBench"]),
            ]
        )
        writer.finish()

        event = storage.get_event("ner", 1)
        assert event is not None
        assert event.title == "Climate Policy Dataset Study"

        doc_ids = [event.doc_id for event in storage.iter_events("ner")]
        assert doc_ids == [0, 1]
