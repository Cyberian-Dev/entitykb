import asyncio
from typing import Optional, List

from entitykb import (
    Direction,
    Doc,
    Edge,
    Entity,
    NeighborResponse,
    Node,
    NodeKey,
    SearchResponse,
    Traversal,
    interfaces,
    istr,
    User,
)
from .client_sync import SyncKB


class AsyncKB(interfaces.IKnowledgeBase):
    def __init__(self, *, host=None, port=None, timeout=None):
        self.sync = SyncKB(host=host, port=port, timeout=timeout)
        self.loop = asyncio.get_event_loop()

    def __len__(self):
        pass

    # nodes

    async def get_node(self, key: str) -> Optional[Node]:
        return await self.loop.run_in_executor(None, self.sync.get_node, key)

    async def save_node(self, node: Node) -> Node:
        return await self.loop.run_in_executor(None, self.sync.save_node, node)

    async def remove_node(self, key) -> Node:
        return await self.loop.run_in_executor(
            None, self.sync.remove_node, key
        )

    async def get_neighbors(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        label: str = None,
        offset: int = 0,
        limit: int = 10,
    ) -> NeighborResponse:

        return await self.loop.run_in_executor(
            None,
            self.sync.get_neighbors,
            node_key,
            verb,
            direction,
            label,
            offset,
            limit,
        )

    async def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[Edge]:

        return await self.loop.run_in_executor(
            None,
            self.sync.get_edges,
            node_key,
            verb,
            direction,
            limit,
        )

    async def count_nodes(self, term=None, labels: istr = None):
        return await self.loop.run_in_executor(
            None,
            self.sync.count_nodes,
            term,
            labels,
        )

    # edges

    async def save_edge(self, edge: Edge):
        return await self.loop.run_in_executor(
            None,
            self.sync.save_edge,
            edge,
        )

    async def connect(
        self, start: Node, verb: str, end: Node, data: dict = None
    ):
        return await self.loop.run_in_executor(
            None,
            self.sync.connect,
            start,
            verb,
            end,
            data,
        )

    # search

    async def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        return await self.loop.run_in_executor(
            None,
            self.sync.parse,
            text,
            labels,
            pipeline,
        )

    async def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        return await self.loop.run_in_executor(
            None,
            self.sync.find,
            text,
            labels,
            pipeline,
        )

    async def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Entity:
        return await self.loop.run_in_executor(
            None,
            self.sync.find_one,
            text,
            labels,
            pipeline,
        )

    async def search(
        self,
        q: str = None,
        labels: istr = None,
        keys: istr = None,
        traversal: Traversal = None,
        limit: int = 100,
        offset: int = 0,
    ) -> SearchResponse:
        return await self.loop.run_in_executor(
            None,
            self.sync.search,
            q,
            labels,
            keys,
            traversal,
            limit,
            offset,
        )

    # admin

    async def transact(self):
        return await self.loop.run_in_executor(
            None,
            self.sync.transact,
        )

    async def reload(self):
        return await self.loop.run_in_executor(
            None,
            self.sync.reload,
        )

    async def reindex(self):
        return await self.loop.run_in_executor(
            None,
            self.sync.reindex,
        )

    async def clear(self) -> bool:
        return await self.loop.run_in_executor(
            None,
            self.sync.clear,
        )

    async def info(self) -> dict:
        return await self.loop.run_in_executor(
            None,
            self.sync.info,
        )

    async def get_schema(self) -> dict:
        return await self.loop.run_in_executor(
            None,
            self.sync.get_schema,
        )

    # users

    async def authenticate(self, username: str, password: str) -> str:
        return await self.loop.run_in_executor(
            None,
            self.sync.authenticate,
            username,
            password,
        )

    async def get_user(self, token: str) -> Optional[User]:
        return await self.loop.run_in_executor(
            None,
            self.sync.get_user,
            token,
        )
