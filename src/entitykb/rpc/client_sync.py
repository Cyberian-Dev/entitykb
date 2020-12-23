import asyncio
from typing import Optional, Union, List

from entitykb import (
    Node,
    ParseRequest,
    Doc,
    SearchRequest,
    SearchResponse,
    Entity,
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

    def parse(self, request: Union[str, ParseRequest]) -> Doc:
        future = super(SyncKB, self).parse(request)
        doc = run_future(future)
        return doc

    def find(self, request: ParseRequest) -> List[Entity]:
        future = super(SyncKB, self).find(request)
        entities = run_future(future)
        return entities

    def find_one(self, request: ParseRequest) -> Entity:
        future = super(SyncKB, self).find_one(request)
        entity = run_future(future)
        return entity

    # graph

    def search(self, request: SearchRequest) -> SearchResponse:
        future = super(SyncKB, self).search(request)
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
