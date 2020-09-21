from dataclasses import dataclass, field
from typing import Iterable, Iterator, Set, List

from . import (
    AttrCriteria,
    Edge,
    FilterStep,
    Graph,
    Node,
    Query,
    RelCriteria,
    WalkStep,
)


class Hop(object):

    __slots__ = ["start", "end", "edges"]

    def __init__(self, start, end, edge: Edge):
        self.start = start
        self.end = end
        self.edges = [edge]


class Result(object):

    __slots__ = ["start", "hops"]

    def __init__(self, start, hops: List[Hop] = None):
        self.start = start
        self.hops: List[Hop] = hops or []

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
        return Result(start=self.start, hops=self.hops[:])

    def push(self, end, edge: Edge) -> "Result":
        copy = self.copy()
        next_hop = Hop(start=self.end, end=end, edge=edge)
        copy.hops.append(next_hop)
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

    @property
    def starts(self):
        return tuple(result.start for result in self.results if result.start)


@dataclass
class Layer(object):
    graph: Graph
    query: Query

    def __iter__(self) -> Iterator[Result]:
        raise NotImplementedError


@dataclass
class StartLayer(Layer):
    starts: Iterable

    def __iter__(self) -> Iterator[Result]:
        for start in self.starts:
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
            others_it = self.graph.iterate_edges(
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

    def evaluate_attr_criteria(self, criteria, result: Result):
        node = self.graph.get_node(result.end)
        other = getattr(node, criteria.attr_name)
        return criteria.do_compare(other)

    def evaluate_rel_criteria(self, criteria, result: Result):
        it = self.graph.iterate_edges(
            tags=criteria.tags,
            directions=criteria.directions,
            nodes=result.end,
        )

        node_set = set(criteria.nodes)

        found = False
        for (key, edge) in it:
            if key in node_set:
                found = True
                break

        return found

    def evaluate_criteria(self, criteria, result: Result):
        if isinstance(criteria, AttrCriteria):
            return self.evaluate_attr_criteria(criteria, result)

        if isinstance(criteria, RelCriteria):
            return self.evaluate_rel_criteria(criteria, result)

        raise NotImplementedError(f"Unknown Criteria: {criteria}")

    def evaluate(self, result: Result):
        success = self.step.all

        for criteria in self.step.criteria:
            if self.step.all:
                success = success and self.evaluate_criteria(criteria, result)
            else:
                success = success or self.evaluate_criteria(criteria, result)

        if self.step.exclude:
            success = not success

        return success

    def __iter__(self) -> Iterator[Result]:
        for result in self.prev:
            if self.evaluate(result):
                yield result


@dataclass
class Searcher(object):
    graph: Graph = None
    query: Query = None

    def __call__(self, *starts, **kwargs):
        return self.search(*starts, **kwargs)

    def search(self, *starts, graph=None, query=None) -> SearchResults:
        """
        Execute search using Query object.
        """
        graph = graph or self.graph
        assert graph, "Graph not provided to searcher."

        query = query or self.query
        assert graph, "Query not provided to searcher."

        starts = chain(starts)
        layer = StartLayer(starts=starts, graph=graph, query=query)

        for step in query.steps:
            if isinstance(step, WalkStep):
                layer = WalkLayer(
                    graph=graph, query=query, step=step, prev=layer
                )
            elif isinstance(step, FilterStep):
                layer = FilterLayer(
                    graph=graph, query=query, step=step, prev=layer
                )

        index = -1
        results = []
        for result in layer:
            index += 1

            if index < query.offset:
                continue

            if under_limit(items=results, limit=query.limit):
                results.append(result)

        return SearchResults(graph=graph, query=query, results=results)


def chain(*items):
    for item in items:
        if isinstance(item, (str, dict)):
            yield item
        elif isinstance(item, (Iterable, Iterator)):
            yield from chain(*item)
        else:
            yield item


def under_limit(items: List, limit: int):
    if limit is None:
        return True

    return len(items) < limit
