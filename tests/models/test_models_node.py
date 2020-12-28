from entitykb.models import Entity, Node, Edge, TripleSep as TS


class CustomNode(Node):
    __default_label__ = "SOMETHING_ELSE"


def test_labels():
    assert Node.get_default_label() == "NODE"
    assert Node.get_all_labels() == {"NODE"}

    assert Entity.get_default_label() == "ENTITY"
    assert Entity.get_all_labels() == {"ENTITY"}

    assert CustomNode.get_default_label() == "SOMETHING_ELSE"
    assert CustomNode.get_all_labels() == {"SOMETHING_ELSE"}


def test_create_node():
    assert isinstance(Node.create(), Node)
    assert isinstance(CustomNode.create(), CustomNode)
    assert Node.create(name="abc").key == "abc|ENTITY"


def test_create_edge():
    edge = Edge(start="a", verb="IS_A", end="b")
    assert edge.dict() == {
        "data": None,
        "end": "b",
        "start": "a",
        "verb": "IS_A",
    }

    assert edge == Edge.create(edge.dict())
    assert edge == Edge.from_line(edge.sve)
    assert edge == Edge.from_line(edge.evs, ts=TS.evs)
