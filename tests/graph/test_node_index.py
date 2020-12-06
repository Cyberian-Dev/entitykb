from entitykb.graph.node_index import NodeIndex
from entitykb.models import Node


def test_node_index():
    node = Node()
    index = NodeIndex()
    index.save(node)
    assert node == index.get(node.key)
    assert {"NODE"} == index.get_labels()

    index.remove(node.key)
    assert index.get(node.key) is None
    assert set() == index.get_labels()
