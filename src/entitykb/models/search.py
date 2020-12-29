from typing import List, Any, Tuple, Optional

from pydantic import BaseModel, Field, validator

from .node import Edge, Node
from .traverse import Traversal
from .enums import Direction


class SearchRequest(BaseModel):
    q: str = None
    labels: Optional[List[str]] = Field(default_factory=list)
    keys: Optional[List[str]] = Field(default_factory=list)
    traversal: Traversal = Field(default_factory=Traversal)
    limit: int = 100
    offset: int = 0

    @validator("traversal", pre=True, always=True)
    def set_traversal(cls, value):
        return Traversal() if value is None else value


class EdgeRequest(BaseModel):
    node_key: str
    verb: str = None
    label: str = None
    direction: Direction = None
    limit: int = 100

    @validator("node_key", pre=True)
    def node_to_key(cls, val):
        return Node.to_key(val)


class Hop(BaseModel):
    start: str
    end: str
    edges: Tuple[Edge, ...] = ()

    def __hash__(self):
        return hash((self.start, self.end, self.edges))

    def __eq__(self, other):
        return (
            self.start == other.start
            and self.end == self.end
            and self.edges == other.edges
        )


class Trail(BaseModel):
    start: str
    hops: Tuple[Hop, ...] = ()

    def __hash__(self):
        return hash((self.start, self.hops and self.hops[-1]))

    def __eq__(self, other):
        return self.start == other.start and self.hops[-1] == other.hops[-1]

    def __repr__(self):
        return f"<Trail: {self.start} - {len(self)} -> {self.end}>"

    def __len__(self):
        return len(self.hops)

    @property
    def end(self):
        if self.hops:
            return self.hops[-1].end
        else:
            return self.start

    def push(self, end, edge: Edge) -> "Trail":
        next_hop = Hop.construct(start=self.end, end=end, edges=(edge,))
        hops = self.hops + (next_hop,)
        return Trail.construct(start=self.start, hops=hops)

    def dict(self, *args, **kwargs):
        return {
            "start": self.start,
            "end": self.end,
            "hops": [hop.dict() for hop in self.hops],
        }


class SearchResponse(BaseModel):
    nodes: List[Node]
    trails: List[Trail]

    def __init__(self, **data: Any):
        nodes = [Node.create(n) for n in data.pop("nodes", [])]
        super().__init__(nodes=[], **data)
        self.nodes = nodes

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, item):
        return self.nodes[item]

    def __iter__(self):
        yield from self.nodes
