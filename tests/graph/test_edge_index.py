from entitykb.graph.edge_index import NestedDict, EdgeIndex
from entitykb.graph.model import Edge, Node


def test_nested_dict():
    nested = NestedDict()
    nested["a"][1]["IS_A"]["b"] = "Edge()"
    assert nested == {"a": {1: {"IS_A": {"b": "Edge()"}}}}


def test_edge_index_save_delete():
    node_a = Node()
    node_b = Node()
    node_c = Node()
    edge_1 = Edge(start=node_b, tag="IS_A", end=node_a, some_val=1)
    edge_2 = Edge(start=node_c, tag="IS_A", end=node_a, some_val=2)

    # add edge 1 or 2
    edge_index = EdgeIndex()
    assert edge_index.save(edge_1)
    assert edge_index.save(edge_2)
    assert not edge_index.save(edge_2)
    assert edge_index.count == 2
    assert len(edge_index.by_node_key) == 3
    assert len(edge_index.by_edge_tag) == 1

    # delete edge 1 (twice)
    edge_index.delete(edge_1)
    assert edge_index.count == 1
    edge_index.delete(edge_1)
    assert edge_index.count == 1
    assert len(edge_index.by_node_key) == 2
    assert len(edge_index.by_edge_tag) == 1

    # delete edge 2 (twice)
    edge_index.delete(edge_2)
    assert edge_index.count == 0
    edge_index.delete(edge_2)
    assert edge_index.count == 0
    assert len(edge_index.by_node_key) == 0
    assert len(edge_index.by_edge_tag) == 0

    assert edge_index.iterate()
