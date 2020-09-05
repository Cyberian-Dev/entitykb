from dataclasses import dataclass, field
from typing import Iterator, Set, List
from .embedded import Graph
from .model import Node, Edge, Query, WalkStep, FilterStep, Filter


class Hop(object):

    __slots__ = ["start", "end", "edges"]

    def __init__(self, start, end, edge: Edge):
        self.start = start
        self.end = end
        self.edges = [edge]


class Result(object):

    __slots__ = ["start", "hops", "by_end"]

    def __init__(self, start, hops: List[Hop] = None, by_end: dict = None):
        self.start = start
        self.hops: List[Hop] = hops or []
        self.by_end = by_end or {}

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __repr__(self):
        return f"<Result: {self.start} - {len(self)} -> {self.end}>"

    def __len__(self):
        return len(self.hops)

    @property
    def end(self):
        if self.hops:
            return self.hops[-1].end
        else:
            return self.start

    def copy(self):
        return Result(
            start=self.start, hops=self.hops[:], by_end=self.by_end.copy(),
        )

    def push(self, end, edge: Edge) -> "Result":
        curr_hop: Hop = self.by_end.get(end, None)

        if curr_hop is None:
            copy = self.copy()
            next_hop = Hop(start=self.end, end=end, edge=edge)
            copy.hops.append(next_hop)
        else:
            curr_hop.edges.append(edge)
            copy = self

        return copy


@dataclass
class SearchResults(object):
    graph: Graph
    query: Query
    results: List[Result]

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return iter(self.results)

    def __getitem__(self, index: int):
        return self.results[index]

    @property
    def ends(self):
        return tuple(result.end for result in self.results if result.end)


@dataclass
class Layer(object):
    graph: Graph
    query: Query

    def __iter__(self) -> Iterator[Result]:
        raise NotImplementedError


@dataclass
class StartLayer(Layer):
    def __iter__(self) -> Iterator[Result]:
        for start in self.query.starts:
            start = Node.to_key(start)
            yield Result(start=start)


@dataclass
class WalkLayer(Layer):
    step: WalkStep
    prev: Layer
    seen: Set = field(default_factory=set)

    def descend(self, result: Result):
        children = set()

        if result.end is not None:
            others_it = self.graph.edges.iterate(
                tags=self.step.tags,
                directions=self.step.directions,
                nodes=result.end,
            )

            for (end, edge) in others_it:
                next_result = result.push(end=end, edge=edge)
                if next_result not in self.seen:
                    self.seen.add(next_result)
                    children.add(next_result)

                    if under_limit(next_result.hops, self.step.max_hops):
                        yield from self.descend(next_result)

        # yield last, handle case of parallel rel w/ multiple tags
        yield from children

    def __iter__(self) -> Iterator[Result]:
        for result in self.prev:
            if self.step.passthru:
                yield result

            self.seen.add(result)

            yield from self.descend(result)


@dataclass
class FilterLayer(Layer):
    step: FilterStep
    prev: Layer

    def evaluate_filter(self, filter: Filter, result: Result):
        # todo: need to figure out how to apply different types of labels...
        return True

    def evaluate(self, result: Result):
        success = self.step.is_and
        for filter in self.step.filters:
            if self.step.is_and:
                success = success and self.evaluate_filter(filter, result)
            else:
                success = success or self.evaluate_filter(filter, result)

        if self.step.exclude:
            success = not success

        return success

    def __iter__(self) -> Iterator[Result]:
        for result in self.prev:
            if self.evaluate(result):
                yield result


@dataclass
class Searcher(object):
    graph: Graph

    def __call__(self, query: Query):
        return self.search(query)

    def search(self, query: Query) -> SearchResults:
        """
        Execute search using Query object.
        """
        layer = StartLayer(graph=self.graph, query=query)

        for step in query.steps:
            if isinstance(step, WalkStep):
                layer = WalkLayer(
                    graph=self.graph, query=query, step=step, prev=layer
                )
            elif isinstance(step, FilterStep):
                layer = FilterLayer(
                    graph=self.graph, query=query, step=step, prev=layer
                )

        index = -1
        results = []
        for result in layer:
            index += 1

            if index < query.offset:
                continue

            if under_limit(items=results, limit=query.limit):
                results.append(result)

        return SearchResults(graph=self.graph, query=query, results=results)


def under_limit(items: List, limit: int):
    if limit is None:
        return True

    return len(items) < limit
