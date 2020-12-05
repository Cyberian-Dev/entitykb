from entitykb import InMemoryGraph, Node, Edge


def test_connect_nodes():
    graph = InMemoryGraph()
    start = Node()
    end = Node()
    other = Node()
    another = Node()

    edge = graph.connect(start=start, verb="NEIGHBORS", end=end)
    assert isinstance(edge, Edge)
    assert graph.info() == {
        "nodes": 2,
        "edges": 1,
    }

    assert 2 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 1 == len(list(graph.edges.iterate("NEIGHBORS", nodes=start)))

    edge2 = graph.connect(start=end, verb="NEIGHBORS", end=start)
    assert isinstance(edge2, Edge)
    assert graph.info() == {
        "nodes": 2,
        "edges": 2,
    }

    assert 4 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 2 == len(list(graph.edges.iterate("NEIGHBORS", nodes=start)))

    graph.connect(start=start, verb="NEIGHBORS", end=other)
    assert 6 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 1 == len(list(graph.edges.iterate("NEIGHBORS", nodes=other)))

    graph.connect(start=start, verb="NEIGHBORS", end=another)

    graph.remove_node(end.key)
    assert graph.info() == {
        "nodes": 3,
        "edges": 2,
    }

    graph.remove_node(start)
    assert graph.info() == {
        "nodes": 2,
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
