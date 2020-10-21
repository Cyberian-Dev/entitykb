import asyncio

import aio_msgpack_rpc

from entitykb import logger, KB, BaseKB, Node
from .connection import RPCConnection


class HandlerKB(BaseKB):
    """ EntityKB RPC Handler Server """

    def __init__(self, _kb):
        self._kb: KB = _kb
        logger.info(f"Handler initialized with {self._kb.config.root}")

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
        data = self._kb.info()
        return data


class RPCServer(object):
    def __init__(self, root: str = None, host: str = None, port: int = None):
        self.conn = RPCConnection(host=host, port=port)
        self.kb = KB(root=root)
        self.handler = HandlerKB(self.kb)
        self.rpc_server = aio_msgpack_rpc.Server(handler=self.handler)
        self.loop: asyncio.AbstractEventLoop = None
        self.stream: asyncio.StreamWriter = None

    def __call__(self, *args, **kwargs):
        return self.serve()

    def serve(self):
        self.loop = asyncio.get_event_loop()
        logger.info(f"Loading Local Knowledge Base: {self.kb.config}")
        logger.info(f"Launching RPC Server on {self.conn}")
        future = asyncio.start_server(
            self.rpc_server, self.conn.host, self.conn.port, loop=self.loop
        )
        self.stream = self.loop.run_until_complete(future)
        self.loop.run_forever()

    def close(self):
        if self.stream:
            logger.info("User terminated. Exiting RPC Server.")
            self.stream.close()
            self.loop.run_until_complete(self.stream.wait_closed())


def launch(root: str = None, host: str = None, port: int = None):
    server = RPCServer(root=root, host=host, port=port)
    try:
        server.serve()
    except KeyboardInterrupt:
        server.close()
