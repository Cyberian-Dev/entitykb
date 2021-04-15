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


class SyncKB(AsyncKB):
    """ EntityKB RPC Client """

    def __len__(self):
        pass

    # nodes

    def get_node(self, key: str) -> Optional[Node]:
        future = super(SyncKB, self).get_node(key)
        node = asyncio.run(future)
        return node

    def save_node(self, node: Node) -> Node:
        future = super(SyncKB, self).save_node(node)
        node = asyncio.run(future)
        return node

    def remove_node(self, key: str) -> Node:
        future = super(SyncKB, self).remove_node(key)
        node = asyncio.run(future)
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
        future = super(SyncKB, self).get_neighbors(
            node_key, verb, direction, label, offset, limit
        )
        neighbors = asyncio.run(future)
        return neighbors

    async def count_nodes(self, term=None, labels: istr = None):
        future = super(SyncKB, self).count_nodes(term, labels)
        count = asyncio.run(future)
        return count

    # edges

    def save_edge(self, edge: Edge):
        future = super(SyncKB, self).save_edge(edge)
        edge = asyncio.run(future)
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
        edges = asyncio.run(future)
        return edges

    # pipeline

    def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        future = super(SyncKB, self).parse(
            text=text, labels=labels, pipeline=pipeline
        )
        doc = asyncio.run(future)
        return doc

    def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        future = super(SyncKB, self).parse(
            text=text, labels=labels, pipeline=pipeline
        )
        doc = asyncio.run(future)
        return doc.entities

    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Entity:
        future = super(SyncKB, self).parse(
            text=text, labels=labels, pipeline=pipeline
        )
        doc = asyncio.run(future)
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

        doc = asyncio.run(future)
        return doc

    # admin

    def reindex(self):
        future = super(SyncKB, self).reindex()
        success = asyncio.run(future)
        return success

    def clear(self) -> bool:
        future = super(SyncKB, self).clear()
        success = asyncio.run(future)
        return success

    def reload(self) -> bool:
        future = super(SyncKB, self).reload()
        success = asyncio.run(future)
        return success

    def info(self) -> dict:
        future = super(SyncKB, self).info()
        data = asyncio.run(future)
        return data

    def get_schema(self) -> dict:
        future = super(SyncKB, self).get_schema()
        data = asyncio.run(future)
        return data

    def authenticate(self, username: str, password: str) -> str:
        future = super(SyncKB, self).authenticate(username, password)
        data = asyncio.run(future)
        return data

    def get_user(self, token: str) -> Optional[User]:
        future = super(SyncKB, self).get_user(token=token)
        data = asyncio.run(future)
        return data
