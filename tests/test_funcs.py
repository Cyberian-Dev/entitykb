from entitykb.models import get_class_from_name, ensure_iterable, Entity


def test_get_class_from_name():
    assert Entity == get_class_from_name("entitykb.Entity")
    assert Entity == get_class_from_name("entitykb.models.Entity")


def test_ensure_iterable():
    assert (1,) == ensure_iterable(1)
    assert ("abc",) == ensure_iterable("abc")
    assert [1, "abc"] == ensure_iterable([1, "abc"])
    assert (1, 2) == ensure_iterable([{1, 2}], explode_first=True)
