from entitykb.graph.index import NodeIndex, EdgeIndex
from entitykb.models import Node, Edge, Direction


def test_node_index():
    node = Node()
    index = NodeIndex()
    index.save(node)
    assert node == index.get(node.key)


def test_edge_index_save_remove():
    node_a = Node()
    node_b = Node()
    node_c = Node()
    edge_1 = Edge(start=node_b, verb="IS_A", end=node_a)
    edge_2 = Edge(start=node_c, verb="IS_A", end=node_a)

    # add edge 1 or 2
    index = EdgeIndex()
    assert index.save(edge_1)
    assert index.save(edge_2)
    assert not index.save(edge_2)
    assert index.count == 2

    # iterate edges
    assert 4 == len(list(index.iterate(verbs="IS_A")))
    print(list(index.iterate(nodes=node_b)))
    assert 1 == len(list(index.iterate(nodes=node_b)))
    assert 2 == len(list(index.iterate(nodes=node_a)))
    assert 2 == len(
        list(index.iterate(nodes=node_a, directions=Direction.incoming))
    )
    assert 0 == len(
        list(index.iterate(nodes=node_a, directions=Direction.outgoing))
    )
    assert 2 == len(
        list(index.iterate(verbs="IS_A", directions=Direction.incoming))
    )
    assert 2 == len(
        list(index.iterate(verbs="IS_A", directions=Direction.outgoing))
    )
    assert 2 == len(
        list(
            index.iterate(
                verbs="IS_A", directions=Direction.incoming, nodes=node_a
            )
        )
    )

    # remove edge 1 (twice)
    index.remove(edge_1)
    assert index.count == 1
    index.remove(edge_1)
    assert index.count == 1

    # remove edge 2 (twice)
    index.remove(edge_2)
    assert index.count == 0
    index.remove(edge_2)
    assert index.count == 0
