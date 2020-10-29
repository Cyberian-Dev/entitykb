from typing import List, Iterator
from .node import Edge
from .entity import Entity
from pydantic import BaseModel


class FindResult(BaseModel):
    term: str
    entities: List[Entity] = []

    def __repr__(self):
        keys = ", ".join(map(lambda e: e.key, self.entities))
        return f"{self.term} [{keys}]"

    def __len__(self):
        return len(self.entities)

    def __iter__(self):
        return iter(self.entities)


class SearchHop(BaseModel):
    start: str
    end: str
    edges: List[Edge] = []


class SearchResult(BaseModel):
    start: str
    hops: List[SearchHop] = []

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __repr__(self):
        return f"<SearchResult: {self.start} - {len(self)} -> {self.end}>"

    def __len__(self):
        return len(self.hops)

    @property
    def end(self):
        if self.hops:
            return self.hops[-1].end
        else:
            return self.start

    def copy(self, **kwargs):
        return SearchResult(start=self.start, hops=self.hops[:])

    def push(self, end, edge: Edge) -> "SearchResult":
        copy = self.copy()
        next_hop = SearchHop(start=self.end, end=end, edges=[edge])
        copy.hops.append(next_hop)
        return copy


class SearchResults(BaseModel):
    results: List[SearchResult]

    def __len__(self):
        return len(self.results)

    def __iter__(self) -> Iterator[SearchResult]:
        return iter(self.results)

    def __getitem__(self, index: int):
        return self.results[index]

    @property
    def ends(self):
        return tuple(result.end for result in self.results if result.end)

    @property
    def starts(self):
        return tuple(result.start for result in self.results if result.start)
