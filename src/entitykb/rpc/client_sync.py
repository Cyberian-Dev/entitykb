import asyncio
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
    User,
    istr,
)
from .client_async import AsyncKB


def run_future(future):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(future)
    return result


class SyncKB(AsyncKB):
    """ EntityKB RPC Client """

    def __len__(self):
        pass

    # nodes

    def get_node(self, key: str) -> Optional[Node]:
        future = super(SyncKB, self).get_node(key)
        node = run_future(future)
        return node

    def save_node(self, node: Node) -> Node:
        future = super(SyncKB, self).save_node(node)
        node = run_future(future)
        return node

    def remove_node(self, key: str) -> Node:
        future = super(SyncKB, self).remove_node(key)
        node = run_future(future)
        return node

    def get_neighbors(
        self,
        node_key: NodeKey,
        verb: str = None,
        label: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[Node]:
        future = super(SyncKB, self).get_neighbors(
            node_key, verb, label, direction, limit
        )
        neighbors = run_future(future)
        return neighbors

    # edges

    def save_edge(self, edge: Edge):
        future = super(SyncKB, self).save_edge(edge)
        edge = run_future(future)
        return edge

    def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[Edge]:
        future = super(SyncKB, self).get_edges(
            node_key, verb, direction, limit
        )
        edges = run_future(future)
        return edges

    # pipeline

    def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        future = super(SyncKB, self).parse(
            text=text, labels=labels, pipeline=pipeline
        )
        doc = run_future(future)
        return doc

    def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        future = super(SyncKB, self).parse(
            text=text, labels=labels, pipeline=pipeline
        )
        doc = run_future(future)
        return doc.entities

    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Entity:
        future = super(SyncKB, self).parse(
            text=text, labels=labels, pipeline=pipeline
        )
        doc = run_future(future)
        return doc.entities[0] if len(doc.entities) == 1 else None

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

        future = super(SyncKB, self).search(
            q=q,
            labels=labels,
            keys=keys,
            traversal=traversal,
            limit=limit,
            offset=offset,
        )

        doc = run_future(future)
        return doc

    # admin

    def reindex(self):
        future = super(SyncKB, self).reindex()
        success = run_future(future)
        return success

    def clear(self) -> bool:
        future = super(SyncKB, self).clear()
        success = run_future(future)
        return success

    def reload(self) -> bool:
        future = super(SyncKB, self).reload()
        success = run_future(future)
        return success

    def info(self) -> dict:
        future = super(SyncKB, self).info()
        data = run_future(future)
        return data

    def get_schema(self) -> dict:
        future = super(SyncKB, self).get_schema()
        data = run_future(future)
        return data

    def authenticate(self, username: str, password: str) -> str:
        future = super(SyncKB, self).authenticate(username, password)
        data = run_future(future)
        return data

    def get_user(self, token: str) -> Optional[User]:
        future = super(SyncKB, self).get_user(token=token)
        data = run_future(future)
        return data
