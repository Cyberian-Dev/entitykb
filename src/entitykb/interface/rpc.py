import asyncio

import uvloop
from aiorpc import RPCClient, register, serve

import entitykb
from entitykb.model import Doc, Entity, Node, Resource, Relationship
from . import BaseKB, KB, const


def get_rpc(host: str = None, port: int = None) -> RPCClient:
    host = host or const.DEFAULT_RPC_HOST
    port = port or const.DEFAULT_RPC_PORT
    return RPCClient(host, port)


class AsyncKB(BaseKB):
    def __init__(self, host: str = None, port: int = None):
        self.rpc = get_rpc(host, port)

    async def parse(self, text, *labels) -> Doc:
        async with self.rpc as client:
            data: dict = await client.call("parse", text, *labels)
            return Doc(**data)

    async def save_entity(self, entity: Entity):
        async with self.rpc as client:
            await client.call("save_entity", entity.dict())

    async def save_resource(self, resource):
        pass

    async def save_relationship(self, a, tag, b):
        pass

    async def commit(self):
        async with self.rpc as client:
            await client.call("commit")


class SyncKB(BaseKB):
    """ EntityKB RPC Client """

    def __init__(self, host: str = None, port: int = None):
        self.async_kb = AsyncKB(host=host, port=port)

    @classmethod
    def _run_future(cls, future):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(future)
        return result

    def parse(self, text: str, *labels: str) -> Doc:
        future = self.async_kb.parse(text, *labels)
        doc = self._run_future(future)
        return doc

    def save_entity(self, entity: Entity) -> bool:
        future = self.async_kb.save_entity(entity)
        doc = self._run_future(future)
        return doc

    def save_resource(self, resource: Resource) -> bool:
        pass

    def save_relationship(self, a: Node, tag: str, b: Node) -> Relationship:
        pass

    def commit(self):
        future = self.async_kb.commit()
        self._run_future(future)


class RPCServerKB(BaseKB):
    """ EntityKB RPC Server """

    def __init__(self, _kb):
        self._kb: KB = _kb

    def parse(self, text: str, *labels: str):
        doc = self._kb.parse(text, *labels)
        return doc.dict()

    def save_entity(self, entity: dict):
        entitykb.logger.warn(f"save_entity: {entity}")
        entity = Entity(**entity)
        self._kb.save_entity(entity)

    def save_resource(self, resource: dict):
        pass

    def save_relationship(self, a: dict, tag: str, to_node: dict):
        pass

    def commit(self):
        self._kb.commit()


def launch_rpc():
    # create proxy
    core = entitykb.load()
    kb = KB(core=core)
    proxy = RPCServerKB(kb)

    # register rpc end-points
    register("parse", proxy.parse)
    register("save_entity", proxy.save_entity)
    register("commit", proxy.commit)

    # host/port config
    host = const.DEFAULT_RPC_HOST
    port = const.DEFAULT_RPC_PORT
    entitykb.logger.warn(f"Launching RPC Server on {host}:{port}")

    # start server
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    future = asyncio.start_server(serve, host, port, loop=loop)
    server = loop.run_until_complete(future)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
        loop.run_until_complete(server.wait_closed())
