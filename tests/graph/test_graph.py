from entitykb import InMemoryGraph, Node, Edge


def test_connect_nodes():
    graph = InMemoryGraph()
    start = Node()

    edge = graph.connect(start=start, tag="IS_A", end=Node())
    assert isinstance(edge, Edge)

    assert start == graph.get_node(start.key)
    assert graph.info() == {
        "nodes": 2,
        "edges": 1,
    }

    graph.remove_node(start.key)
    assert graph.info() == {
        "nodes": 1,
        "edges": 0,
    }


def test_clear_info():
    graph = InMemoryGraph()

    graph.save_node(node=Node())
    assert graph.info() == {
        "nodes": 1,
        "edges": 0,
    }

    graph.clear_data()
    assert graph.info() == {
        "nodes": 0,
        "edges": 0,
    }
