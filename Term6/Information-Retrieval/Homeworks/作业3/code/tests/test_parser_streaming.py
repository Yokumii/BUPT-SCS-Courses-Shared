"""
测试 parser 的流式解析接口。
"""

from src.parser import iter_documents


def _write_doc(path, title, abstract, body):
    path.write_text(
        f"Title: {title}\n"
        "Journal: Test Journal\n"
        "Publication Date: 2024\n"
        "Authors: A, B\n"
        "Abstract:\n"
        f"{abstract}\n\n"
        "I. Introduction\n"
        f"{body}\n"
        "DOI: 10.1/test\n",
        encoding="utf-8",
    )


def _long_text(seed: str) -> str:
    return " ".join([seed] * 40)


def test_iter_documents_filters_and_reassigns_doc_ids(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _write_doc(
        data_dir / "a.txt",
        "Valid One",
        _long_text("This abstract contains enough words to be considered substantive."),
        _long_text("This body text is also long enough to pass the substantive document filter."),
    )
    _write_doc(
        data_dir / "b.txt",
        "Erratum",
        "short",
        "short",
    )
    _write_doc(
        data_dir / "c.txt",
        "Valid Two",
        _long_text("Another abstract containing enough useful text for parsing."),
        _long_text("Another sufficiently long body for the second document."),
    )

    docs = list(iter_documents(str(data_dir), verbose=False))
    assert [doc.doc_id for doc in docs] == [0, 1]
    assert [doc.title for doc in docs] == ["Valid One", "Valid Two"]
