from msgpack import packb, unpackb

from entitykb.models import Edge, Node
from pydantic.json import pydantic_encoder


def test_node():
    empty = Node()
    assert 36 == len(empty.key)
    assert empty.dict() == dict(key=empty.key, label="NODE", data=None)

    node = Node(key="ENTITY|LABEL", label="LABEL")
    assert node.dict() == dict(key="ENTITY|LABEL", label="LABEL", data=None)

    data = packb(node, default=pydantic_encoder)
    assert unpackb(data, object_hook=Node.create) == node


def test_edge():
    start = Node()
    end = Node()
    edge = Edge(start=start, end=end, verb="IS_A")
    assert edge.dict() == {
        "start": start.key,
        "verb": "IS_A",
        "end": end.key,
        "data": None,
    }

    two = start >> "IS_A" >> end
    assert two == edge
    assert two.dict() == edge.dict()

    three = end << "IS_A" << start
    assert three == edge
    assert three.dict() == edge.dict()

    edge.set_verb("HAS_A")
    assert edge.dict() == {
        "start": start.key,
        "verb": "HAS_A",
        "end": end.key,
        "data": None,
    }

    data = dict(a="b")
    edge.set_data(data)
    assert edge.dict() == {
        "start": start.key,
        "verb": "HAS_A",
        "end": end.key,
        "data": {"a": "b"},
    }
