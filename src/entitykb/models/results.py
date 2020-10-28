from typing import List
from .base import SlotBase
from .node import Edge


class FindResult(SlotBase):

    __slots__ = ("term", "entities")

    def __init__(self, term: str, entities=None):
        self.term = term
        self.entities = entities or ()

    def __repr__(self):
        keys = ", ".join(map(lambda e: e.key, self.entities))
        return f"{self.term} [{keys}]"

    def __len__(self):
        return len(self.entities)

    def __iter__(self):
        return iter(self.entities)


class SearchHop(object):

    __slots__ = ["start", "end", "edges"]

    def __init__(self, start, end, edge: Edge):
        self.start = start
        self.end = end
        self.edges = [edge]


class SearchResult(object):

    __slots__ = ["start", "hops"]

    def __init__(self, start, hops: List[SearchHop] = None):
        self.start = start
        self.hops: List[SearchHop] = hops or []

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

    def copy(self):
        return SearchResult(start=self.start, hops=self.hops[:])

    def push(self, end, edge: Edge) -> "SearchResult":
        copy = self.copy()
        next_hop = SearchHop(start=self.end, end=end, edge=edge)
        copy.hops.append(next_hop)
        return copy


class SearchResults(object):
    __slots__ = ["results"]

    def __init__(self, results: List[SearchResult]):
        self.results = results

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return iter(self.results)

    def __getitem__(self, index: int):
        return self.results[index]

    @property
    def ends(self):
        return tuple(result.end for result in self.results if result.end)

    @property
    def starts(self):
        return tuple(result.start for result in self.results if result.start)
