from entitykb.models.funcs import camel_to_snake, ensure_iterable, label_filter


def test_ensure_iterable():
    assert (1,) == ensure_iterable(1)
    assert ("abc",) == ensure_iterable("abc")
    assert [1, "abc"] == ensure_iterable([1, "abc"])
    assert (1, 2) == ensure_iterable([{1, 2}], explode_first=True)


def test_label_filter():
    f = label_filter(["A", "B", "C"])
    r = filter(f, ["0|A", "4|X", "5|Y", "1|B", "2|B"])
    assert ["0|A", "1|B", "2|B"] == list(r)


def test_camel_to_snake():
    assert "CUSTOM_NODE" == camel_to_snake("CustomNode", upper=True)
    assert "abc_def_ghi" == camel_to_snake("AbcDefGhi")
