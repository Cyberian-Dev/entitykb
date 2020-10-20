from entitykb import Graph, Node, Edge


def test_connect_nodes():
    graph = Graph()
    start = Node()

    edge = graph.connect(start=start, tag="IS_A", end=Node(), some_val=1)
    assert isinstance(edge, Edge)

    assert start == graph.get_node(start.key)
    assert graph.info() == {
        "nodes": 2,
        "edges": 1,
    }


def test_reset_info():
    graph = Graph()

    graph.save_node(node=Node())
    assert graph.info() == {
        "nodes": 1,
        "edges": 0,
    }

    graph.reset_data()
    assert graph.info() == {
        "nodes": 0,
        "edges": 0,
    }
