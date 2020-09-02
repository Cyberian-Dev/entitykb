from entitykb.graph.embedded import NestedDict, Graph
from entitykb.graph.model import Node, Edge


def test_nested_dict():
    ddds = NestedDict()
    ddds["a"][1]["IS_A"]["b"] = "Edge()"
    assert ddds == {"a": {1: {"IS_A": {"b": "Edge()"}}}}


def test_connect_nodes():
    graph = Graph()
    edge = graph.connect(start=Node(), tag="IS_A", end=Node(), some_val=1)
    assert isinstance(edge, Edge)
