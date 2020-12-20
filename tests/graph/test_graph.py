from entitykb import Edge, Graph, Node


def test_connect_remove_nodes_edges(root, normalizer):
    graph = Graph(root=root, normalizer=normalizer)
    start = Node()
    end = Node()
    other = Node()
    another = Node()

    edge = graph.connect(start=start, verb="NEIGHBORS", end=end)
    assert graph.info() == dict(nodes=2, edges=1)

    graph.reindex()
    assert 2 == len(list(graph.iterate_edges(verbs="NEIGHBORS")))
    assert 1 == len(list(graph.iterate_edges("NEIGHBORS", nodes=start)))

    edge2 = graph.connect(start=end, verb="NEIGHBORS", end=start)
    assert isinstance(edge2, Edge)
    assert graph.info() == dict(nodes=2, edges=2)

    graph.reindex()
    assert 4 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 2 == len(list(graph.edges.iterate("NEIGHBORS", nodes=start)))

    graph.connect(start=start, verb="NEIGHBORS", end=other)
    assert graph.info() == dict(nodes=3, edges=3)

    graph.reindex()
    assert 6 == len(list(graph.edges.iterate("NEIGHBORS")))
    assert 1 == len(list(graph.edges.iterate("NEIGHBORS", nodes=other)))

    graph.connect(start=start, verb="NEIGHBORS", end=another)
    assert graph.info() == dict(nodes=4, edges=4)

    graph.remove_edge(edge)
    assert graph.info() == dict(nodes=4, edges=3)

    graph.remove_node(other)
    assert graph.info() == dict(nodes=3, edges=3)

    graph.remove_node(end)
    assert graph.info() == dict(nodes=2, edges=3)

    graph.remove_node(another)
    assert graph.info() == dict(nodes=1, edges=3)

    graph.reindex()
    assert graph.info() == dict(nodes=1, edges=3)

    graph.remove_edges(other)
    assert graph.info() == dict(nodes=1, edges=2)

    graph.clean_edges()
    assert graph.info() == dict(nodes=1, edges=0)


def test_clear_info(root, normalizer):
    graph = Graph(root, normalizer)
    graph.save_node(node=Node())
    graph.reindex()

    assert graph.info() == {
        "nodes": 1,
        "edges": 0,
    }

    graph.clear()
    graph.reindex()

    assert graph.info() == {
        "nodes": 0,
        "edges": 0,
    }
