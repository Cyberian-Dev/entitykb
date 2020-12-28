import asyncio
from typing import Optional, List

from entitykb import (
    Doc,
    Entity,
    Node,
    SearchResponse,
    Traversal,
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

    def remove_node(self, key) -> Node:
        future = super(SyncKB, self).remove_node(key)
        node = run_future(future)
        return node

    # edges

    def save_edge(self, edge):
        future = super(SyncKB, self).save_edge(edge)
        edge = run_future(future)
        return edge

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
        future = super(SyncKB, self).find(
            text=text, labels=labels, pipeline=pipeline
        )
        entities = run_future(future)
        return entities

    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Entity:
        future = super(SyncKB, self).find_one(
            text=text, labels=labels, pipeline=pipeline
        )
        entity = run_future(future)
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
