"""
测试 spaCy 管线缓存行为。
"""

from src import nlp_pipeline


class _FakeModel:
    max_length = 1000

    def __call__(self, text):
        return text


def test_get_nlp_cache_isolated_by_disabled_components(monkeypatch):
    calls = []

    def fake_load(model_name, disable=None):
        calls.append((model_name, tuple(disable or ())))
        return _FakeModel()

    monkeypatch.setattr(nlp_pipeline, "spacy", type("FakeSpacy", (), {"load": staticmethod(fake_load)}))
    nlp_pipeline._nlp_instances.clear()

    first = nlp_pipeline.get_nlp("en_core_web_sm", disable=("ner",))
    second = nlp_pipeline.get_nlp("en_core_web_sm", disable=("ner",))
    third = nlp_pipeline.get_nlp("en_core_web_sm", disable=())

    assert first is second
    assert third is not first
    assert calls == [
        ("en_core_web_sm", ("ner",)),
        ("en_core_web_sm", ()),
    ]
