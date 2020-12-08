from entitykb.models import Node, Edge


def test_node():
    empty = Node()
    assert 36 == len(empty.key)
    assert empty.dict() == dict(key=empty.key, label="NODE", data=None)

    node = Node(key="ENTITY|LABEL", label="LABEL")
    assert node.dict() == dict(key="ENTITY|LABEL", label="LABEL", data=None)


def test_edge():
    start = Node()
    end = Node()
    edge = Edge(start=start, end=end, verb="IS_A")
    assert edge.dict() == dict(__root__=(start.key, "IS_A", end.key))

    two = start >> "IS_A" >> end
    assert two == edge
    assert two.dict() == edge.dict()

    three = end << "IS_A" << start
    assert three == edge
    assert three.dict() == edge.dict()
