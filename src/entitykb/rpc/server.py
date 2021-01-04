import asyncio
import os
from typing import Optional, List

import aio_msgpack_rpc
from msgpack import Packer, Unpacker

from entitykb import (
    logger,
    KB,
    ParseRequest,
    SearchRequest,
    EdgeRequest,
)
from .connection import RPCConnection


class HandlerKB(object):
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

    def remove_node(self, key) -> dict:
        node = self._kb.remove_node(key)
        return node.dict()

    def get_neighbors(self, request: dict) -> List[dict]:
        request = EdgeRequest(**request)
        nodes = self._kb.get_neighbors(
            node_key=request.node_key,
            verb=request.verb,
            label=request.label,
            direction=request.direction,
            limit=request.limit,
        )
        return [node.dict() for node in nodes]

    def get_edges(self, request: dict) -> List[dict]:
        request = EdgeRequest(**request)
        edges = self._kb.get_edges(
            node_key=request.node_key,
            verb=request.verb,
            direction=request.direction,
            limit=request.limit,
        )
        return [edge.dict() for edge in edges]

    # edges

    def save_edge(self, edge: dict):
        edge = self._kb.save_edge(edge)
        return edge.dict()

    # pipeline

    def parse(self, request: dict) -> dict:
        request = ParseRequest(**request)
        doc = self._kb.parse(
            text=request.text, labels=request.labels, pipeline=request.pipeline
        )
        return doc.dict()

    def find(self, request: dict) -> List[dict]:
        request = ParseRequest(**request)
        doc = self._kb.parse(
            text=request.text, labels=request.labels, pipeline=request.pipeline
        )
        return [s.entity.dict() for s in doc.spans if s and s.entity]

    def find_one(self, request: dict) -> dict:
        request = ParseRequest(**request)
        doc = self._kb.parse(
            text=request.text, labels=request.labels, pipeline=request.pipeline
        )
        return doc.entities[0].dict() if len(doc.entities) == 1 else None

    # graph

    def search(self, request: dict) -> dict:
        request = SearchRequest(**request)
        response = self._kb.search(
            q=request.q,
            labels=request.labels,
            keys=request.keys,
            traversal=request.traversal,
            limit=request.limit,
            offset=request.offset,
        )
        return response.dict()

    # admin

    def transact(self):
        pass

    def reload(self):
        self._kb.reload()

    def reindex(self):
        self._kb.reindex()

    def clear(self) -> bool:
        success = self._kb.clear()
        return success

    def info(self) -> dict:
        data = self._kb.info()
        return data

    def get_schema(self) -> dict:
        data = self._kb.get_schema()
        return data

    # users

    def authenticate(self, username: str, password: str) -> str:
        """ Check username password combo, return user's uuid if valid. """
        return self._kb.authenticate(username=username, password=password)

    def get_user(self, token: str) -> Optional[dict]:
        """ Return user for valid token from authenticate. """
        user = self._kb.get_user(token=token)
        if user:
            return user.dict()


class RPCServer(object):
    def __init__(self, root: str = None, host: str = None, port: int = None):
        self.connection = RPCConnection(host=host, port=port)
        self.kb = KB(root=root)
        self.handler = HandlerKB(self.kb)
        self.rpc_server = aio_msgpack_rpc.Server(
            handler=self.handler,
            packer=Packer(use_bin_type=True, datetime=True),
            unpacker_factory=lambda: Unpacker(raw=False, timestamp=3),
        )
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.stream: Optional[asyncio.StreamWriter] = None

    def __call__(self, *args, **kwargs):
        return self.serve()

    def serve(self):
        self.loop = asyncio.get_event_loop()

        logger.info(f"Process ID: {os.getpid()}")
        logger.info(f"EntityKB Root: {self.kb.config.root}")
        logger.info(f"RPC Server LAUNCHED {self.connection}")

        future = asyncio.start_server(
            self.rpc_server,
            self.connection.host,
            self.connection.port,
            loop=self.loop,
        )
        self.stream = self.loop.run_until_complete(future)
        self.loop.run_forever()

    def close(self):
        logger.info(
            f"RPC Server EXITING {self.connection} for {self.kb.config}"
        )
        if self.stream:
            self.stream.close()
            self.loop.run_until_complete(self.stream.wait_closed())


def launch(root: str = None, host: str = None, port: int = None):
    server = RPCServer(root=root, host=host, port=port)
    try:
        server.serve()
    except KeyboardInterrupt:
        server.close()
