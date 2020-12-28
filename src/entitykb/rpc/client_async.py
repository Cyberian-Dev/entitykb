from typing import Optional, List

from entitykb import (
    Doc,
    Entity,
    Node,
    ParseRequest,
    SearchRequest,
    SearchResponse,
    Traversal,
    interfaces,
    istr,
)
from .connection import RPCConnection


class AsyncKB(interfaces.IKnowledgeBase):
    def __init__(self, *, host=None, port=None, timeout=None):
        self.connection = RPCConnection(host=host, port=port, timeout=timeout)

    def __len__(self):
        raise NotImplementedError

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    # nodes

    async def get_node(self, key: str) -> Optional[Node]:
        async with self.connection as client:
            node = await client.call("get_node", key)
            node = Node.create(node) if node else None
            return node

    async def save_node(self, node: Node) -> Node:
        async with self.connection as client:
            return await client.call("save_node", node.dict())

    async def remove_node(self, key) -> Node:
        async with self.connection as client:
            return await client.call("remove_node", key)

    # edges

    async def save_edge(self, edge):
        async with self.connection as client:
            return await client.call("save_edge", edge.dict())

    # search

    async def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        request = ParseRequest(text=text, labels=labels, pipeline=pipeline)
        async with self.connection as client:
            data: dict = await client.call("parse", request.dict())
            return Doc(**data)

    async def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        doc = await self.parse(text=text, labels=labels, pipeline=pipeline)
        return doc.entities

    async def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Entity:
        entities = await self.find(text=text, labels=labels, pipeline=pipeline)
        return entities[0] if len(entities) == 1 else None

    async def search(
        self,
        q: str = None,
        labels: istr = None,
        keys: istr = None,
        traversal: Traversal = None,
        limit: int = 100,
        offset: int = 0,
    ) -> SearchResponse:

        request = SearchRequest(
            q=q,
            labels=labels,
            keys=keys,
            traversal=traversal,
            limit=limit,
            offset=offset,
        )

        async with self.connection as client:
            data: dict = await client.call("search", request.dict())
            return SearchResponse(**data)

    # admin

    async def transact(self):
        async with self.connection as client:
            return await client.call("transact")

    async def reload(self):
        async with self.connection as client:
            return await client.call("reload")

    async def reindex(self):
        async with self.connection as client:
            return await client.call("reindex")

    async def clear(self) -> bool:
        async with self.connection as client:
            return await client.call("clear")

    async def info(self) -> dict:
        async with self.connection as client:
            return await client.call("info")

    async def get_schema(self) -> dict:
        async with self.connection as client:
            return await client.call("get_schema")
