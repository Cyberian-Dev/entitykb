from dataclasses import dataclass, field
from typing import List, Dict, Set

from . import EID, Graph, Query


@dataclass
class Hop(object):
    graph: Graph
    start_id: EID
    end_id: EID
    tags: Set[str]

    def start(self):
        return self.graph.get_entity_key(self.start_id)

    def end(self):
        return self.graph.get_entity_key(self.end_id)

    def dict(self):
        return dict(start=self.start, end=self.end, tags=sorted(self.tags))


@dataclass
class Result(object):
    graph: Graph
    start_id: EID
    hops: List[Hop] = field(default_factory=list)
    by_end_id: Dict[EID, Hop] = field(default_factory=dict)

    def __repr__(self):
        return f"<Result: {self.start} - {len(self)} -> {self.end}>"

    def __len__(self):
        return len(self.hops)

    def __hash__(self):
        return hash((self.start_id, self.end_id))

    def __eq__(self, other):
        return self.start_id == other.start_id and self.end_id == other.end_id

    def copy(self):
        return Result(
            graph=self.graph,
            start_id=self.start_id,
            hops=self.hops[:],
            by_end_id=self.by_end_id,
        )

    def push(self, tag: str, end_id: EID) -> "Result":
        curr_hop = self.by_end_id.get(end_id, None)

        if curr_hop is None:
            copy = self.copy()
            next_hop = Hop(
                graph=self.graph,
                start_id=self.end_id,
                end_id=end_id,
                tags={tag},
            )
            copy.hops.append(next_hop)
        else:
            curr_hop.tags.add(tag)
            copy = self

        return copy

    @property
    def end_id(self):
        if self.hops:
            return self.hops[-1].end_id
        else:
            return self.start_id

    @property
    def start(self):
        return self.graph.get_entity_key(self.start_id)

    @property
    def end(self):
        return self.graph.get_entity_key(self.end_id)

    @property
    def entity(self):
        return self.graph.get_entity(self.end_id)

    def dict(self):
        hops = []
        for hop in self.hops:
            hops.append(hop.dict())

        return dict(start=self.start, end=self.end, hops=hops)


@dataclass
class SearchResults(object):
    graph: Graph
    query: Query
    results: List[Result]

    def __getitem__(self, index: int):
        return self.results[index]

    def __iter__(self):
        return iter(self.results)

    def __len__(self):
        return len(self.results)

    def dict(self):
        results = [result.dict() for result in self.results]
        return dict(query=self.query.dict(), results=results)

    @property
    def entities(self):
        return tuple(result.entity for result in self.results)
