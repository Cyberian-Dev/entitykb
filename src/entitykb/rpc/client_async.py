from entitykb.kb import BaseKB
from entitykb.model import Doc, Entity
from .connection import RPCConnection


class AsyncKB(BaseKB):
    def __init__(self, *, connection=None, host=None, port=None, timeout=None):
        self.connection = connection or RPCConnection(
            host=host, port=port, timeout=timeout
        )

    async def parse(self, text, *labels):
        async with self.connection as client:
            data: dict = await client.call("parse", text, *labels)
            return Doc(**data)

    async def search(self, query):
        pass

    async def suggest(self, query):
        pass

    async def commit(self):
        async with self.connection as client:
            count: int = await client.call("commit")
            return count

    async def reset(self):
        async with self.connection as client:
            return await client.call("reset")

    async def reload(self):
        pass

    async def info(self):
        async with self.connection as client:
            return await client.call("info")

    async def save_entity(self, entity: Entity):
        async with self.connection as client:
            await client.call("save_entity", entity.dict())

    async def get_entity(self, key_or_id):
        pass

    async def delete_entity(self, key_or_id):
        pass

    async def save_resource(self, resource):
        pass

    async def get_resource(self, key_or_id):
        pass

    async def delete_resource(self, key_or_id):
        pass

    async def save_relationship(self, relationship):
        pass

    async def delete_relationship(self, relationship):
        pass
