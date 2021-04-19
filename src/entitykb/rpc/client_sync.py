from typing import Optional, List

from entitykb import (
    Direction,
    Doc,
    Edge,
    Entity,
    Node,
    NodeKey,
    SearchResponse,
    Traversal,
    istr,
)
from .client_proxy import ProxyKB


class SyncKB(ProxyKB):
    """ EntityKB RPC Client """

    # nodes

    def get_node(self, key: str) -> Optional[Node]:
        node = super(SyncKB, self).get_node(key)
        node = Node.create(node) if node else None
        return node

    def save_node(self, node: Node) -> Node:
        node = super(SyncKB, self).save_node(node)
        node = Node.create(node) if node else None
        return node

    def remove_node(self, key: str) -> Node:
        node = super(SyncKB, self).remove_node(key)
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
    ) -> List[Node]:
        neighbors = super(SyncKB, self).get_neighbors(
            node_key=node_key,
            verb=verb,
            direction=direction,
            label=label,
            offset=offset,
            limit=limit,
        )
        return [Node.create(neighbor) for neighbor in neighbors]

    # edges

    def save_edge(self, edge: Edge) -> Edge:
        edge = super(SyncKB, self).save_edge(edge)
        return Edge.create(edge) if edge else None

    def connect(self, start: Node, verb: str, end: Node, data: dict = None):
        edge = super(SyncKB, self).connect(start, verb, end, data)
        return Edge.create(edge) if edge else None

    def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[Edge]:
        edges = super(SyncKB, self).get_edges(
            node_key=node_key, verb=verb, direction=direction, limit=limit
        )
        return [Edge.create(edge) for edge in edges]

    # pipeline

    def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        data = super(SyncKB, self).parse(
            text, labels=labels, pipeline=pipeline
        )
        return Doc(**data)

    def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        entities = super(SyncKB, self).find(
            text, labels=labels, pipeline=pipeline
        )
        return [Entity.create(**entity) for entity in entities]

    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Optional[Entity]:
        entity = super(SyncKB, self).find_one(
            text, labels=labels, pipeline=pipeline
        )
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
        response = super(SyncKB, self).search(
            q=q,
            labels=labels,
            keys=keys,
            traversal=traversal,
            limit=limit,
            offset=offset,
        )
        return SearchResponse(**response)
