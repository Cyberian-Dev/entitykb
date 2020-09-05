from .edge_index import EdgeIndex
from .model import Node, Edge


class Graph(object):
    def __init__(self):
        self.nodes = {}
        self.edges = EdgeIndex()

    def __repr__(self):
        n, e = len(self.nodes), len(self.edges)
        return f"<Graph: {n} nodes, {e} edges>"

    def __iter__(self):
        return iter(self.nodes.values())

    def save_node(self, node: Node):
        self.nodes[node.key] = node

    def get_node(self, key: str):
        return self.nodes[key]

    def connect(self, *, start: Node, tag: str, end: Node, **meta):
        edge = Edge(start=start, tag=tag, end=end, meta=meta)
        self.save_edge(edge)
        return edge

    def save_edge(self, edge: Edge):
        self.edges.save(edge)
