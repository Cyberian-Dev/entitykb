import os
import asyncio
from typing import Optional

import aio_msgpack_rpc

from entitykb import logger, KB, BaseKB, ParseRequest, SearchRequest
from .connection import RPCConnection


class HandlerKB(BaseKB):
    """ EntityKB RPC Handler Server """

    def __init__(self, _kb):
        self._kb: KB = _kb

    def __len__(self):
        raise NotImplementedError

    # nodes

    def get_node(self, key: str) -> Optional[dict]:
        node = self._kb.get_node(key)
        data = None if node is None else node.dict()
        return data

    def save_node(self, node) -> dict:
        node = self._kb.save_node(node)
        return node.dict()

    def remove_node(self, key) -> bool:
        return self._kb.remove_node(key)

    # edges

    def save_edge(self, edge):
        edge = self._kb.save_edge(edge)
        return edge.dict()

    # pipeline

    def parse(self, request: dict) -> dict:
        request = ParseRequest(**request)
        doc = self._kb.parse(request)
        return doc.dict()

    # graph

    def search(self, request: dict) -> dict:
        request = SearchRequest(**request)
        response = self._kb.search(request)
        return response.dict()

    # admin

    def commit(self) -> bool:
        count = self._kb.commit()
        return count

    def clear(self) -> bool:
        success = self._kb.clear()
        return success

    def reload(self) -> bool:
        success = self._kb.reload()
        return success

    def info(self) -> dict:
        data = self._kb.info()
        return data

    def get_schema(self) -> dict:
        data = self._kb.get_schema()
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

        logger.info(f"Process ID: {os.getpid()}")
        logger.info(f"EntityKB Root: {self.kb.config.root}")
        logger.info(f"RPC Server LAUNCHED {self.conn}")

        future = asyncio.start_server(
            self.rpc_server, self.conn.host, self.conn.port, loop=self.loop
        )
        self.stream = self.loop.run_until_complete(future)
        self.loop.run_forever()

    def close(self):
        logger.info(f"RPC Server EXITING {self.conn} for {self.kb.config}")
        if self.stream:
            self.stream.close()
            self.loop.run_until_complete(self.stream.wait_closed())


def launch(root: str = None, host: str = None, port: int = None):
    server = RPCServer(root=root, host=host, port=port)
    try:
        server.serve()
    except KeyboardInterrupt:
        server.close()
