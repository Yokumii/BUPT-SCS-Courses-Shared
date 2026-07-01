"""
测试 build_ie 的分批抽取写入流程。
"""

from build_ie import run_extraction
from src.ie_storage import IEStorage
from src.schema import AcademicPaperEvent


def _long_text(seed: str) -> str:
    return " ".join([seed] * 40)


def _write_doc(path, title, abstract, body):
    path.write_text(
        f"Title: {title}\n"
        "Journal: Test Journal\n"
        "Publication Date: 2024\n"
        "Authors: Test University\n"
        "Abstract:\n"
        f"{abstract}\n\n"
        "I. Introduction\n"
        f"{body}\n"
        "DOI: 10.1/test\n",
        encoding="utf-8",
    )


def test_run_extraction_writes_regex_results_to_sqlite(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "index" / "ie"
    data_dir.mkdir(parents=True)

    _write_doc(
        data_dir / "doc0.txt",
        "Transformer Study",
        _long_text("We achieved 95 accuracy on the ImageNet dataset using Transformer."),
        _long_text("Researchers from Test University found that the method improves performance."),
    )

    storage = IEStorage(output_dir)
    run_extraction(
        str(data_dir),
        methods=["regex"],
        storage=storage,
        limit=0,
        batch_size=10,
        verbose=False,
    )

    summaries = storage.list_method_summaries()
    assert summaries["regex"]["total_docs"] == 1
    event = storage.get_event("regex", 0)
    assert event is not None
    assert event.title == "Transformer Study"


def test_run_extraction_supports_multiple_methods_in_one_run(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "index" / "ie"
    data_dir.mkdir(parents=True)

    _write_doc(
        data_dir / "doc0.txt",
        "Transformer Study",
        _long_text("We achieved 95 accuracy on the ImageNet dataset using Transformer."),
        _long_text("Researchers from Test University found that the method improves performance."),
    )

    class _FakeExtractor:
        def __init__(self, method: str):
            self._method = method

        def extract_batch(self, documents, verbose=False):
            return [
                AcademicPaperEvent(
                    doc_id=doc.doc_id,
                    title=doc.title,
                    extraction_method=self._method,
                )
                for doc in documents
            ]

    from build_ie import get_extractor as _real_get_extractor
    import build_ie

    def fake_get_extractor(method: str):
        if method in {"regex", "ner"}:
            return _FakeExtractor(method)
        return _real_get_extractor(method)

    storage = IEStorage(output_dir)
    monkeypatch.setattr(build_ie, "get_extractor", fake_get_extractor)
    run_extraction(
        str(data_dir),
        methods=["regex", "ner"],
        storage=storage,
        limit=0,
        batch_size=10,
        verbose=False,
    )

    summaries = storage.list_method_summaries()
    assert summaries["regex"]["total_docs"] == 1
    assert summaries["ner"]["total_docs"] == 1
