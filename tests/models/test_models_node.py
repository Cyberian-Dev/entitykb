from entitykb import Node, Entity


class CustomNode(Node):
    pass


def test_default_label():
    assert CustomNode.__dict__.get("__default_label__") is None
    assert "CUSTOM_NODE" == CustomNode.get_default_label()


def test_identify_klass():
    assert Node.identify_klass({}) is None
    assert Node.identify_klass(dict(key=1)) is None
    assert Node.identify_klass(dict(label="ENTITY")) == Entity
    assert Node.identify_klass(dict(name="Entity Name")) == Entity
    assert Node.identify_klass(dict(label="CUSTOM_NODE")) == CustomNode


def round_trip_create():
    custom_node = CustomNode()
    data = custom_node.dict()
    roundtrip = Node.create(data)
    assert isinstance(roundtrip, CustomNode)
    assert roundtrip.key == custom_node.key
