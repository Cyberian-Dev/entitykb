from dataclasses import dataclass, field
from typing import Iterable, Iterator, Set, List

from entitykb.models import (
    FieldCriteria,
    FilterStep,
    Node,
    Query,
    EdgeCriteria,
    SearchResult,
    SearchResults,
    WalkStep,
    chain,
)
from . import Graph


@dataclass
class Layer(object):
    graph: Graph

    def __iter__(self) -> Iterator[SearchResult]:
        raise NotImplementedError


@dataclass
class StartLayer(Layer):
    starts: Iterable

    def __iter__(self) -> Iterator[SearchResult]:
        for start in self.starts:
            start = Node.to_key(start)
            yield SearchResult(start=start)


@dataclass
class WalkLayer(Layer):
    step: WalkStep
    prev: Layer
    seen: Set = field(default_factory=set)

    def descend(self, result: SearchResult):
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

    def __iter__(self) -> Iterator[SearchResult]:
        for result in self.prev:
            if self.step.passthru:
                yield result

            self.seen.add(result)

            yield from self.descend(result)


@dataclass
class FilterLayer(Layer):
    step: FilterStep
    prev: Layer

    def evaluate_attr_criteria(self, criteria, result: SearchResult):
        node = self.graph.get_node(result.end)
        try:
            other = getattr(node, criteria.attr_name)
            return criteria.do_compare(other)
        except AttributeError:
            return False

    def evaluate_rel_criteria(self, criteria, result: SearchResult):
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

    def evaluate_criteria(self, criteria, result: SearchResult):
        if isinstance(criteria, FieldCriteria):
            return self.evaluate_attr_criteria(criteria, result)

        if isinstance(criteria, EdgeCriteria):
            return self.evaluate_rel_criteria(criteria, result)

        raise NotImplementedError(f"Unknown Criteria: {criteria}")

    def evaluate(self, result: SearchResult):
        success = self.step.all

        for criteria in self.step.criteria:
            if self.step.all:
                success = success and self.evaluate_criteria(criteria, result)
            else:
                success = success or self.evaluate_criteria(criteria, result)

        if self.step.exclude:
            success = not success

        return success

    def __iter__(self) -> Iterator[SearchResult]:
        for result in self.prev:
            if self.evaluate(result):
                yield result


@dataclass
class Searcher(object):
    graph: Graph = None

    def __call__(self, query: Query, *starts):
        return self.search(query, *starts)

    def search(self, query: Query, *starts) -> SearchResults:
        starts = chain(starts)
        layer = StartLayer(self.graph, starts=starts)

        for step in query.steps:
            if isinstance(step, WalkStep):
                layer = WalkLayer(graph=self.graph, step=step, prev=layer)
            elif isinstance(step, FilterStep):
                layer = FilterLayer(graph=self.graph, step=step, prev=layer)

        index = -1
        results = []
        for result in layer:
            index += 1

            if index < query.offset:
                continue

            if under_limit(items=results, limit=query.limit):
                results.append(result)

        return SearchResults(results=results)


def under_limit(items: List, limit: int):
    if limit is None:
        return True

    return len(items) < limit
