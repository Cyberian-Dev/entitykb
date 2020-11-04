from typing import List

from pydantic import BaseModel

from .enums import SearchInput
from .node import Edge
from .query import Query


class SearchRequest(BaseModel):
    q: str = None
    input: SearchInput = SearchInput.prefix
    query: Query = None


class Hop(BaseModel):
    start: str
    end: str
    edges: List[Edge] = []


class Trail(BaseModel):
    start: str
    hops: List[Hop] = []

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

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

    def copy(self, **kwargs):
        return Trail(start=self.start, hops=self.hops[:])

    def push(self, end, edge: Edge) -> "Trail":
        copy = self.copy()
        next_hop = Hop(start=self.end, end=end, edges=[edge])
        copy.hops.append(next_hop)
        return copy

    def dict(self, *args, **kwargs):
        return {
            "start": self.start,
            "end": self.end,
            "hops": [hop.dict() for hop in self.hops],
        }


class SearchResponse(BaseModel):
    nodes: List[dict]
    trails: List[Trail]
