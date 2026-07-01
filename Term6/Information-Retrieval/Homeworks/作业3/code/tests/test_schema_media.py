from src.schema import AcademicPaperEvent


def test_event_serialization_preserves_doi():
    event = AcademicPaperEvent(
        doc_id=1,
        title="Demo Paper",
        doi="10.123/demo",
        methods=["regression"],
    )

    restored = AcademicPaperEvent.from_dict(event.to_dict())

    assert restored.doi == "10.123/demo"


def test_event_merge_preserves_doi():
    first = AcademicPaperEvent(doc_id=1, title="Demo Paper", doi="10.123/demo")
    second = AcademicPaperEvent(doc_id=1, title="Demo Paper", methods=["BERT"])

    merged = first.merge(second)

    assert merged.doi == "10.123/demo"
    assert merged.methods == ["BERT"]
