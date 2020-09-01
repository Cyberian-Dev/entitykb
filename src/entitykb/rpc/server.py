import asyncio

from aio_msgpack_rpc import Server

from entitykb import logger, KB
from entitykb.kb import BaseKB
from entitykb.model import Entity
from .connection import RPCConnection


class HandlerKB(BaseKB):
    """ EntityKB RPC Handler Server """

    def __init__(self, _kb):
        self._kb: KB = _kb

    def parse(self, text: str, *labels: str) -> dict:
        doc = self._kb.parse(text, *labels)
        return doc.dict()

    def search(self, query):
        pass

    def suggest(self, query):
        pass

    def commit(self):
        count = self._kb.commit()
        return count

    def reset(self):
        success = self._kb.reset()
        return success

    def reload(self):
        pass

    def info(self):
        data = self._kb.info()
        return data

    def save_entity(self, entity: dict):
        logger.info(f"save_entity: {entity}")
        entity = Entity(**entity)
        self._kb.save_entity(entity)

    def get_entity(self, key_or_id):
        pass

    def delete_entity(self, key_or_id):
        pass

    def save_resource(self, resource: dict):
        pass

    def get_resource(self, key_or_id):
        pass

    def delete_resource(self, key_or_id):
        pass

    def save_relationship(self, relationship: dict):
        pass

    def delete_relationship(self, relationship: dict):
        pass


def launch_rpc(root_dir: str = None, host: str = None, port: int = None):
    """ Function for starting RPC Server. Called from entitykb CLI. """
    conn = RPCConnection(host=host, port=port)
    kb = KB(root_dir=root_dir)
    handler = HandlerKB(kb)
    server = Server(handler=handler)

    loop = asyncio.get_event_loop()
    logger.info(f"Launching RPC Server on {conn}")
    future = asyncio.start_server(server, conn.host, conn.port, loop=loop)
    server = loop.run_until_complete(future)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
        loop.run_until_complete(server.wait_closed())
