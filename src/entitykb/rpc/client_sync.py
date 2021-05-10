from typing import Optional, List

from entitykb import (
    Direction,
    Doc,
    Edge,
    Entity,
    NeighborResponse,
    Node,
    NodeKey,
    SearchResponse,
    Traversal,
    interfaces,
    istr,
    User,
)
from .client_proxy import ProxyKB


class SyncKB(interfaces.IKnowledgeBase):
    """ EntityKB RPC Client """

    def __init__(self, *, host=None, port=None, timeout=None):
        self.proxy = ProxyKB(host=host, port=port, timeout=timeout)

    def __len__(self):
        pass

    # nodes

    def get_node(self, key: str) -> Optional[Node]:
        node = self.proxy.get_node(key)
        node = Node.create(node) if node else None
        return node

    def save_node(self, node: Node) -> Node:
        node = self.proxy.save_node(node)
        node = Node.create(node) if node else None
        return node

    def remove_node(self, key: str) -> Node:
        node = self.proxy.remove_node(key)
        node = Node.create(node) if node else None
        return node

    def get_neighbors(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        label: str = None,
        offset: int = 0,
        limit: int = 10,
    ) -> NeighborResponse:
        neighbor_response = self.proxy.get_neighbors(
            node_key=node_key,
            verb=verb,
            direction=direction,
            label=label,
            offset=offset,
            limit=limit,
        )

        return NeighborResponse(**neighbor_response)

    def count_nodes(self, term=None, labels: istr = None):
        return self.proxy.count_nodes(term=term, labels=labels)

    # edges

    def save_edge(self, edge: Edge) -> Edge:
        edge = self.proxy.save_edge(edge)
        return Edge.create(edge) if edge else None

    def connect(self, start: Node, verb: str, end: Node, data: dict = None):
        edge = self.proxy.connect(start, verb, end, data)
        return Edge.create(edge) if edge else None

    def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[Edge]:
        edges = self.proxy.get_edges(
            node_key=node_key, verb=verb, direction=direction, limit=limit
        )
        return [Edge.create(edge) for edge in edges]

    # pipeline

    def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        data = self.proxy.parse(text, labels=labels, pipeline=pipeline)
        return Doc(**data)

    def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        entities = self.proxy.find(text, labels=labels, pipeline=pipeline)
        return [Entity.create(**entity) for entity in entities]

    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Optional[Entity]:
        entity = self.proxy.find_one(text, labels=labels, pipeline=pipeline)
        entity = Entity.create(**entity) if entity else None
        return entity

    # graph

    def search(
        self,
        q: str = None,
        labels: istr = None,
        keys: istr = None,
        traversal: Traversal = None,
        limit: int = 100,
        offset: int = 0,
    ) -> SearchResponse:
        response = self.proxy.search(
            q=q,
            labels=labels,
            keys=keys,
            traversal=traversal,
            limit=limit,
            offset=offset,
        )
        return SearchResponse(**response)

    # admin

    def transact(self):
        return self.proxy.transact()

    def reload(self):
        return self.proxy.reload()

    def reindex(self):
        return self.proxy.reindex()

    def clear(self):
        return self.proxy.clear()

    def info(self) -> dict:
        return self.proxy.info()

    def get_schema(self) -> dict:
        return self.proxy.get_schema()

    def authenticate(self, username: str, password: str) -> Optional[str]:
        return self.proxy.authenticate(username, password)

    def get_user(self, token: str) -> Optional[User]:
        return self.proxy.get_user(token)
