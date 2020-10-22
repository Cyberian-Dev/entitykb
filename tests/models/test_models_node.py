from entitykb import Node


class CustomNode(Node):
    pass


def test_default_label():
    assert CustomNode.__dict__.get("__default_label__") is None
    assert "CUSTOM_NODE" == CustomNode.get_default_label()


def round_trip_create():
    custom_node = CustomNode()
    data = custom_node.dict()
    roundtrip = Node.create(data)
    assert isinstance(roundtrip, CustomNode)
    assert roundtrip.key == custom_node.key
