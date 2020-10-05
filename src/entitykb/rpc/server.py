import asyncio

from aio_msgpack_rpc import Server

from entitykb import logger, KB, BaseKB, Node
from .connection import RPCConnection


class HandlerKB(BaseKB):
    """ EntityKB RPC Handler Server """

    def __init__(self, _kb):
        self._kb: KB = _kb
        logger.info(f"Handler initialized with {self._kb.config.root_dir}")

    def __len__(self):
        raise NotImplementedError

    def get_node(self, key: str) -> dict:
        node = self._kb.get_node(key)
        data = node.dict()
        return data

    def save_node(self, node) -> int:
        node = Node.create(node)
        return self._kb.save_node(node)

    def remove_node(self, key):
        raise NotImplementedError

    def save_edge(self, edge):
        raise NotImplementedError

    def suggest(self, term, query=None):
        raise NotImplementedError

    def parse(self, text, labels=None) -> dict:
        doc = self._kb.parse(text, labels)
        return doc.dict()

    def commit(self):
        try:
            count = self._kb.commit()
            return count
        except Exception as e:
            logger.exception(e)
            raise e

    def reset(self):
        success = self._kb.reset()
        return success

    def reload(self):
        raise NotImplementedError

    def info(self):
        logger.info("call received: info()")
        data = self._kb.info()
        return data


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
    logger.info(f"Server info: {handler.info()}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
        loop.run_until_complete(server.wait_closed())
