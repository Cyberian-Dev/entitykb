from entitykb import BaseKB, Doc, Node
from .connection import RPCConnection


class AsyncKB(BaseKB):

    def __init__(self, *, connection=None, host=None, port=None, timeout=None):
        self.connection = connection or RPCConnection(
            host=host, port=port, timeout=timeout
        )

    def __len__(self):
        raise NotImplementedError

    async def get_node(self, key: str):
        async with self.connection as client:
            data: dict = await client.call("get_node", key)
            return Node(**data)

    async def save_node(self, node: Node):
        async with self.connection as client:
            await client.call("save_node", node.dict())

    async def remove_node(self, key):
        raise NotImplementedError

    async def save_edge(self, edge):
        raise NotImplementedError

    async def suggest(self, term, query=None):
        raise NotImplementedError

    async def parse(self, text, labels=None):
        async with self.connection as client:
            data: dict = await client.call("parse", text, labels=labels)
            return Doc(**data)

    async def commit(self):
        async with self.connection as client:
            count: int = await client.call("commit")
            return count

    async def reset(self):
        async with self.connection as client:
            return await client.call("reset")

    async def reload(self):
        raise NotImplementedError

    async def info(self):
        async with self.connection as client:
            return await client.call("info")
