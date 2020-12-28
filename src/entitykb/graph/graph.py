from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Set, Optional, Tuple

from entitykb import Node, NodeKey, Edge, interfaces, istr
from . import EdgeIndex, NodeIndex


class Graph(interfaces.IGraph):
    def __init__(self, root: Path, normalizer: interfaces.INormalizer):
        super().__init__(root, normalizer)
        self.nodes = NodeIndex(root=root, normalizer=normalizer)
        self.edges = EdgeIndex(root=root)

    def __repr__(self):
        return f"<Graph: {len(self.nodes)} nodes, {len(self.edges)} edges>"

    def __len__(self) -> int:
        return len(self.nodes)

    def __iter__(self) -> Iterable[Node]:
        yield from self.iterate_nodes()

    def save_node(self, node: Node):
        self.nodes.save(node)

    def get_node(self, key: str) -> Node:
        return self.nodes.get(key=key)

    def remove_node(self, node_key: NodeKey) -> Node:
        return self.nodes.remove(node_key)

    def get_labels(self) -> Set[str]:
        return self.nodes.get_labels()

    def save_edge(self, edge: Edge):
        return self.edges.save(edge)

    def remove_edge(self, edge: Edge) -> Optional[dict]:
        return self.edges.remove(edge)

    def remove_edges(self, node: NodeKey) -> int:
        key = Node.to_key(node)
        count = 0
        for _, edge in self.edges.iterate(nodes=key):
            self.edges.remove(edge)
            count += 1
        return count

    def connect(self, *, start: Node, verb: str, end: Node, data: dict = None):
        self.save_node(start)
        self.save_node(end)
        edge = Edge(start=start, verb=verb, end=end, data=data)
        self.save_edge(edge)
        return edge

    def get_verbs(self) -> Set[str]:
        return self.edges.get_verbs()

    def iterate_edges(
        self, verbs=None, directions=None, nodes=None
    ) -> Iterable[Tuple[str, Edge]]:
        yield from self.edges.iterate(
            verbs=verbs, directions=directions, nodes=nodes
        )

    def iterate_keys(
        self,
        keys: istr = None,
        terms: istr = None,
        prefixes: istr = None,
        labels: istr = None,
    ) -> Iterable[str]:
        yield from self.nodes.iterate(
            keys=keys, terms=terms, prefixes=prefixes, labels=labels
        )

    def iterate_nodes(
        self,
        keys: istr = None,
        terms: istr = None,
        prefixes: istr = None,
        labels: istr = None,
    ) -> Iterable[Node]:

        for key in self.nodes.iterate(
            keys=keys, terms=terms, prefixes=prefixes, labels=labels
        ):
            yield self.nodes.get(key=key)

    @contextmanager
    def transact(self):
        with self.nodes.cache.transact():
            with self.edges.cache.transact():
                yield

    def reindex(self):
        self.edges.reindex()
        self.nodes.reindex()

    def reload(self):
        self.nodes.reload()
        self.edges.reload()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

    def clean_edges(self):
        self.edges.clean(self.nodes)

    def info(self):
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
        }
