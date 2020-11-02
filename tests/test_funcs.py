from entitykb.models import ensure_iterable


def test_ensure_iterable():
    assert (1,) == ensure_iterable(1)
    assert ("abc",) == ensure_iterable("abc")
    assert [1, "abc"] == ensure_iterable([1, "abc"])
    assert (1, 2) == ensure_iterable([{1, 2}], explode_first=True)
