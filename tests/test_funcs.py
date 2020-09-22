from entitykb import funcs, Entity


def test_get_class_from_name():
    cls = funcs.get_class_from_name("entitykb.graph.model.Entity")
    assert cls == Entity


def test_ensure_iterable():
    assert (1,) == funcs.ensure_iterable(1)
    assert ("abc",) == funcs.ensure_iterable("abc")
    assert [1, "abc"] == funcs.ensure_iterable([1, "abc"])
    assert (1, 2) == funcs.ensure_iterable([{1, 2}], explode_first=True)
