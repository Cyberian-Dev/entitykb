from typing import Optional, List, Union

from Pyro5 import api as pyro, config

from entitykb import (
    Direction,
    Edge,
    NodeKey,
    Traversal,
    User,
    environ,
    interfaces,
    istr,
)

# reference: https://pyro5.readthedocs.io/en/latest/config.html
config.SERIALIZER = "msgpack"


class ProxyKB(interfaces.IKnowledgeBase):
    """ EntityKB RPC Client that returns raw data types. """

    def __init__(
        self, host: str = None, port: int = None, timeout: int = None
    ):
        host = host or environ.rpc_host
        port = port or environ.rpc_port
        self.url = f"PYRO:kb@{host}:{port}"
        self.timeout = timeout or environ.rpc_timeout

    def __len__(self):
        pass

    # nodes

    def get_node(self, key: str) -> Optional[dict]:
        with pyro.Proxy(self.url) as proxy:
            node = proxy.get_node(key)
            return node

    def save_node(self, node) -> dict:
        with pyro.Proxy(self.url) as proxy:
            node = proxy.save_node(node)
            return node

    def remove_node(self, key: str) -> dict:
        with pyro.Proxy(self.url) as proxy:
            node = proxy.remove_node(key)
            return node

    def get_neighbors(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        label: str = None,
        offset: int = 0,
        limit: int = 10,
    ) -> dict:
        with pyro.Proxy(self.url) as proxy:
            neighbor_response = proxy.get_neighbors(
                node_key=node_key,
                verb=verb,
                direction=direction,
                label=label,
                offset=offset,
                limit=limit,
            )
            return neighbor_response

    def count_nodes(self, term=None, labels: istr = None) -> int:
        with pyro.Proxy(self.url) as proxy:
            return proxy.count_nodes(term, labels)

    # edges

    def save_edge(self, edge: Union[dict, Edge]) -> dict:
        with pyro.Proxy(self.url) as proxy:
            edge = proxy.save_edge(edge)
            return edge

    def connect(self, start, verb: str, end, data: dict = None):
        with pyro.Proxy(self.url) as proxy:
            edge = proxy.connect(start, verb, end, data)
            return edge

    def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[dict]:
        with pyro.Proxy(self.url) as proxy:
            edges = proxy.get_edges(
                node_key=node_key, verb=verb, direction=direction, limit=limit
            )
            return edges

    # pipeline

    def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> dict:
        with pyro.Proxy(self.url) as proxy:
            doc = proxy.parse(text, labels=labels, pipeline=pipeline)
            return doc

    def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[dict]:
        doc = self.parse(text, labels=labels, pipeline=pipeline)
        spans = (doc or {}).get("spans", [])
        return [span.get("entity") for span in spans]

    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> dict:
        entities = self.find(text, labels, pipeline)
        return entities[0] if len(entities) == 1 else None

    # graph

    def search(
        self,
        q: str = None,
        labels: istr = None,
        keys: istr = None,
        traversal: Traversal = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:

        with pyro.Proxy(self.url) as proxy:
            response = proxy.search(
                q=q,
                labels=labels,
                keys=keys,
                traversal=traversal,
                limit=limit,
                offset=offset,
            )
            return response

    # admin

    def transact(self):
        with pyro.Proxy(self.url) as proxy:
            return proxy.transact()

    def reload(self) -> bool:
        with pyro.Proxy(self.url) as proxy:
            return proxy.reload()

    def reindex(self):
        with pyro.Proxy(self.url) as proxy:
            return proxy.reindex()

    def clear(self) -> bool:
        with pyro.Proxy(self.url) as proxy:
            return proxy.clear()

    def info(self) -> dict:
        with pyro.Proxy(self.url) as proxy:
            return proxy.info()

    def get_schema(self) -> dict:
        with pyro.Proxy(self.url) as proxy:
            return proxy.get_schema()

    def authenticate(self, username: str, password: str) -> str:
        with pyro.Proxy(self.url) as proxy:
            return proxy.authenticate(username, password)

    def get_user(self, token: str) -> Optional[User]:
        with pyro.Proxy(self.url) as proxy:
            return proxy.get_user(token)
