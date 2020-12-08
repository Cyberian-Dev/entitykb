from entitykb.graph.nodes import NodeIndex
from entitykb.models import Node


def test_node_index():
    node = Node()
    index = NodeIndex()
    index.save(node)
    index.commit()

    assert node == index.get(node.key)
    assert {"NODE"} == index.get_labels()

    index.remove(node.key)
    index.commit()

    assert index.get(node.key) is None
    assert set() == index.get_labels()
