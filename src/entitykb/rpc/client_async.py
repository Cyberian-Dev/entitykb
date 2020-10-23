from typing import Optional
from entitykb import BaseKB, Doc, Node
from .connection import RPCConnection


class AsyncKB(BaseKB):
    def __init__(self, *, connection=None, host=None, port=None, timeout=None):
        self.connection = connection or RPCConnection(
            host=host, port=port, timeout=timeout
        )

    def __len__(self):
        raise NotImplementedError

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

    async def save_edge(self, edge):
        raise NotImplementedError

    async def suggest(self, term, query=None):
        raise NotImplementedError

    async def parse(self, text, *labels):
        async with self.connection as client:
            data: dict = await client.call("parse", text, *labels)
            return Doc(**data)

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
