from entitykb.models.funcs import camel_to_snake


def test_camel_to_snake():
    assert "CUSTOM_NODE" == camel_to_snake("CustomNode", upper=True)
    assert "abc_def_ghi" == camel_to_snake("AbcDefGhi")
