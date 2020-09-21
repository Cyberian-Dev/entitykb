from entitykb.graph import Graph, Node, Edge


def test_connect_nodes():
    graph = Graph()
    start = Node()
    edge = graph.connect(start=start, tag="IS_A", end=Node(), some_val=1)
    assert isinstance(edge, Edge)

    assert start == graph.get_node(start.key)
