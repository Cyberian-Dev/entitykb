from typing import Optional

from entitykb import (
    BaseKB,
    Node,
    ParseRequest,
    Doc,
    SearchRequest,
    SearchResponse,
)

from .connection import RPCConnection


class AsyncKB(BaseKB):
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

    async def remove_node(self, key) -> bool:
        async with self.connection as client:
            return await client.call("remove_node", key)

    # edges

    async def save_edge(self, edge):
        async with self.connection as client:
            return await client.call("save_edge", edge.dict())

    # search

    async def parse(self, request: ParseRequest) -> Doc:
        async with self.connection as client:
            data: dict = await client.call("parse", request.dict())
            return Doc(**data)

    async def search(self, request: SearchRequest) -> SearchResponse:
        async with self.connection as client:
            data: dict = await client.call("search", request.dict())
            return SearchResponse(**data)

    # admin

    async def commit(self) -> bool:
        async with self.connection as client:
            return await client.call("commit")

    async def clear(self) -> bool:
        async with self.connection as client:
            return await client.call("clear")

    async def reload(self) -> bool:
        async with self.connection as client:
            return await client.call("reload")

    async def info(self) -> dict:
        async with self.connection as client:
            return await client.call("info")

    async def get_schema(self) -> dict:
        async with self.connection as client:
            return await client.call("get_schema")
