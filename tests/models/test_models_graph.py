from entitykb.models import Node, Edge


def test_node():
    empty = Node()
    assert 36 == len(empty.key)
    assert empty.dict() == dict(key=empty.key, label="NODE", attrs={})

    node = Node(key="ENTITY|LABEL", label="LABEL")
    assert node.dict() == dict(key="ENTITY|LABEL", label="LABEL", attrs={},)


def test_edge():
    start = Node()
    end = Node()
    edge = Edge(start=start, end=end, tag="IS_A")
    assert edge.dict() == dict(
        start=start.key, tag="IS_A", end=end.key, weight=1, attrs={},
    )

    two = start >> "IS_A" >> end
    assert two == edge
    assert two.dict() == edge.dict()

    three = end << "IS_A" << start
    assert three == edge
    assert three.dict() == edge.dict()
