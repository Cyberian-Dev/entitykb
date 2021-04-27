import sys
import textwrap
from typing import Optional, List

from Pyro5.api import expose, behavior, serve

from entitykb import (
    Direction,
    KB,
    Node,
    NodeKey,
    Traversal,
    environ,
    istr,
    logger,
)


@expose
@behavior(instance_mode="single")
class ServerKB(object):
    """ EntityKB RPC Handler Server """

    def __init__(self):
        self._kb: KB = KB()

    # nodes

    @logger.timed
    def get_node(self, key: str) -> Optional[dict]:
        node = self._kb.get_node(key)
        data = None if node is None else node.dict()
        return data

    @logger.timed
    def save_node(self, node) -> dict:
        node = self._kb.save_node(node)
        return node.dict()

    @logger.timed
    def remove_node(self, key) -> dict:
        node = self._kb.remove_node(key)
        return node.dict()

    @logger.timed
    def get_neighbors(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        label: str = None,
        offset: int = 0,
        limit: int = 10,
    ) -> dict:
        response = self._kb.get_neighbors(
            node_key=node_key,
            verb=verb,
            direction=direction,
            label=label,
            offset=offset,
            limit=limit,
        )
        return response.dict()

    @logger.timed
    def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[dict]:
        edges = self._kb.get_edges(
            node_key=node_key,
            verb=verb,
            direction=direction,
            limit=limit,
        )
        return [edge.dict() for edge in edges]

    @logger.timed
    def count_nodes(self, term=None, labels: istr = None) -> int:
        return self._kb.count_nodes(term=term, labels=labels)

    # edges

    @logger.timed
    def save_edge(self, edge: dict):
        edge = self._kb.save_edge(edge)
        return edge.dict()

    @logger.timed
    def connect(self, *, start: Node, verb: str, end: Node, data: dict = None):
        edge = self._kb.connect(start=start, verb=verb, end=end, data=data)
        return edge.dict()

    # pipeline

    @logger.timed
    def parse(
        self, text: str, labels: istr = None, pipeline: str = None
    ) -> dict:
        doc = self._kb.parse(text=text, labels=labels, pipeline=pipeline)
        data = doc.dict()
        return data

    @logger.timed
    def find(
        self, text: str, labels: istr = None, pipeline: str = None
    ) -> List[dict]:
        entities = self._kb.find(text=text, labels=labels, pipeline=pipeline)
        return [entity.dict() for entity in entities]

    @logger.timed
    def find_one(
        self, text: str, labels: istr = None, pipeline: str = None
    ) -> dict:
        entity = self._kb.find_one(text=text, labels=labels, pipeline=pipeline)
        return entity and entity.dict()

    # graph

    @logger.timed
    def search(
        self,
        q: str = None,
        labels: istr = None,
        keys: istr = None,
        traversal: Traversal = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        response = self._kb.search(
            q=q,
            labels=labels,
            keys=keys,
            traversal=traversal,
            limit=limit,
            offset=offset,
        )
        return response.dict()

    # admin

    @logger.timed
    def transact(self):
        pass

    @logger.timed
    def reload(self):
        self._kb.reload()

    @logger.timed
    def reindex(self):
        self._kb.reindex()

    @logger.timed
    def clear(self) -> bool:
        success = self._kb.clear()
        return success

    @logger.timed
    def info(self) -> dict:
        data = self._kb.info()
        return data

    @logger.timed
    def get_schema(self) -> dict:
        data = self._kb.get_schema()
        return data

    # users

    @logger.timed
    def authenticate(self, username: str, password: str) -> str:
        """ Check username password combo, return user's uuid if valid. """
        return self._kb.authenticate(username=username, password=password)

    @logger.timed
    def get_user(self, token: str) -> Optional[dict]:
        """ Return user for valid token from authenticate. """
        user = self._kb.get_user(token=token)
        if user:
            return user.dict()


def launch(root: str = None, host: str = None, port: int = None):
    host = host or environ.rpc_host
    port = port or environ.rpc_port
    if root:
        environ.root = root

    python_path = textwrap.indent("\n".join(filter(None, sys.path)), " " * 12)

    logger.info(f"Launching RPC: {host}:{port}")
    logger.info(f"KB Root Path : {environ.root}")
    logger.info(f"Python Path :\n{python_path}")

    serve({ServerKB: "kb"}, use_ns=False, host=host, port=port, verbose=False)
