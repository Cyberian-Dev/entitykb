from entitykb.graph.embedded import Graph
from entitykb.graph.model import Node, Edge


def test_connect_nodes():
    graph = Graph()
    edge = graph.connect(start=Node(), tag="IS_A", end=Node(), some_val=1)
    assert isinstance(edge, Edge)
