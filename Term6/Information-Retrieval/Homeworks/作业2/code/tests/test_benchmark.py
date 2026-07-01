import benchmark


def test_round_optional_preserves_none():
    assert benchmark.round_optional(None, 4) is None
    assert benchmark.round_optional(0.12345, 4) == 0.1235
