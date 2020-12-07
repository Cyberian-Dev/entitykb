from entitykb import InMemoryGraph, Node, Edge


def test_connect_nodes():
    graph = InMemoryGraph()
    start = Node()
    end = Node()
    other = Node()
    another = Node()

    edge = graph.connect(start=start, verb="NEIGHBORS", end=end)
    graph.commit()

    assert isinstance(edge, Edge)
    assert graph.info() == {
        "nodes": 2,
        "edges": 1,
    }

    assert 2 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 1 == len(list(graph.edges.iterate("NEIGHBORS", nodes=start)))

    edge2 = graph.connect(start=end, verb="NEIGHBORS", end=start)
    graph.commit()

    assert isinstance(edge2, Edge)
    assert graph.info() == {
        "nodes": 2,
        "edges": 2,
    }

    assert 4 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 2 == len(list(graph.edges.iterate("NEIGHBORS", nodes=start)))

    graph.connect(start=start, verb="NEIGHBORS", end=other)
    graph.commit()

    assert 6 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 1 == len(list(graph.edges.iterate("NEIGHBORS", nodes=other)))

    graph.connect(start=start, verb="NEIGHBORS", end=another)
    graph.remove_node(end.key)
    graph.commit()

    assert graph.info() == {
        "nodes": 3,
        "edges": 2,
    }

    graph.remove_node(start)
    graph.commit()

    assert graph.info() == {
        "nodes": 2,
        "edges": 0,
    }


def test_clear_info():
    graph = InMemoryGraph()
    graph.save_node(node=Node())
    graph.commit()

    assert graph.info() == {
        "nodes": 1,
        "edges": 0,
    }

    graph.clear_data()
    graph.commit()

    assert graph.info() == {
        "nodes": 0,
        "edges": 0,
    }
