from typing import Tuple, List

from entitykb import (
    Node,
    Edge,
    Registry,
    create_component,
    ensure_iterable,
    label_filter,
)
from .node_index import NodeIndex
from .edge_index import EdgeIndex


class Graph(object):
    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    # nodes

    def iterate_keys(self, keys: List[str] = None, labels: List[str] = None):
        raise NotImplementedError

    def save_node(self, node: Node):
        raise NotImplementedError

    def get_node(self, key: str):
        raise NotImplementedError

    def remove_node(self, key: str) -> bool:
        raise NotImplementedError

    def get_labels(self):
        raise NotImplementedError

    # edges

    def iterate_edges(self, verbs=None, directions=None, nodes=None):
        raise NotImplementedError

    def save_edge(self, edge: Edge):
        raise NotImplementedError

    def connect(self, *, start: Node, verb: str, end: Node, data: dict = None):
        raise NotImplementedError

    def get_verbs(self):
        raise NotImplementedError

    # admin

    def info(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def put_data(self, data):
        raise NotImplementedError

    def clear_data(self):
        raise NotImplementedError

    @classmethod
    def create(cls, value=None):
        return create_component(value, Graph, InMemoryGraph)


class InMemoryGraph(Graph):
    def __init__(self):
        self.nodes = NodeIndex()
        self.edges = EdgeIndex()

    def __repr__(self):
        n, e = len(self.nodes), len(self.edges)
        return f"<Graph: {n} nodes, {e} edges>"

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    # nodes

    def iterate_keys(self, keys: List[str] = None, labels: List[str] = None):
        if not keys and labels:
            for label in labels:
                it = self.nodes.iterate_keys_by_label(label)
                yield from it

        elif keys:
            it = ensure_iterable(keys)
            it = filter(label_filter(labels), it)
            it = filter(lambda k: k in self.nodes, it)
            yield from it

        else:
            it = self.nodes.nodes_by_key.keys()
            yield from it

    def save_node(self, node: Node):
        self.nodes.save(node)

    def get_node(self, key: str):
        return self.nodes.get(key)

    def remove_node(self, key: str) -> Node:
        key = Node.to_key(key)

        # capture all edges to prevent iterator issues
        edges = [edge for _, edge in self.edges.iterate(nodes=[key])]

        for edge in edges:
            self.edges.remove(edge)

        node = self.nodes.remove(key)

        return node

    def get_labels(self):
        return self.nodes.get_labels()

    # edges

    def iterate_edges(self, verbs=None, directions=None, nodes=None):
        yield from self.edges.iterate(
            verbs=verbs, directions=directions, nodes=nodes
        )

    def save_edge(self, edge: Edge):
        self.edges.save(edge)
        return edge

    def connect(self, *, start: Node, verb: str, end: Node, data: dict = None):
        registry = Registry.instance()
        self.save_node(start)
        self.save_node(end)
        edge = registry.create(Edge, data, start=start, verb=verb, end=end)
        self.save_edge(edge)
        return edge

    def get_verbs(self):
        return set(self.edges.get_verbs())

    # admin

    def info(self):
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
        }

    def get_data(self) -> Tuple[NodeIndex, EdgeIndex]:
        return self.nodes, self.edges

    def put_data(self, data: Tuple[NodeIndex, EdgeIndex]):
        self.nodes, self.edges = data

    def clear_data(self):
        self.nodes = NodeIndex()
        self.edges = EdgeIndex()
