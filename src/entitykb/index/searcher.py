from dataclasses import dataclass, field
from typing import Iterator, Set

from .graph import Graph
from .query import (
    Query,
    QueryStart,
    QueryGoal,
    Result,
    SearchResults,
    WalkStep,
    FilterStep,
)


@dataclass
class Layer(object):
    graph: Graph

    def __iter__(self) -> Iterator[Result]:
        raise NotImplementedError


@dataclass
class StartLayer(Layer):
    start: QueryStart

    def __iter__(self) -> Iterator[Result]:
        entity_id_it = self.start.entities or self.graph
        for entity_id in entity_id_it:
            entity_id = self.graph.get_entity_id(entity_id)
            yield Result(graph=self.graph, start_id=entity_id)


@dataclass
class WalkLayer(Layer):
    step: WalkStep
    prev: Layer
    seen: Set = field(default_factory=set)

    def descend(self, result: Result):
        children = set()
        for req_tag in self.step.tags:
            others_it = self.graph.iterate_others(
                tag=req_tag, incoming=self.step.incoming, entity=result.end_id
            )
            for (rel_tag, end_id) in others_it:
                next_result = result.push(tag=rel_tag, end_id=end_id)
                if next_result not in self.seen:
                    self.seen.add(next_result)
                    children.add(next_result)
                    yield from self.descend(next_result)

        # yield last, handle case of parallel rel w/ multiple tags
        yield from children

    def __iter__(self) -> Iterator[Result]:
        for result in self.prev:
            self.seen.add(result)
            yield from self.descend(result)


@dataclass
class FilterLayer(Layer):
    step: FilterStep
    prev: Layer

    def __iter__(self) -> Iterator[Result]:
        for result in self.prev:
            yield result


@dataclass
class GoalLayer(Layer):
    goal: QueryGoal
    prev: Layer

    def __iter__(self) -> Iterator[Result]:
        count = 0

        for result in self.prev:
            if self.goal.limit and count >= self.goal.limit:
                break

            yield result
            count += 1


@dataclass
class Searcher(object):
    graph: Graph

    def search(self, query: Query) -> SearchResults:
        layer = StartLayer(graph=self.graph, start=query.start)

        for step in query.steps:
            if isinstance(step, WalkStep):
                layer = WalkLayer(graph=self.graph, step=step, prev=layer)
            elif isinstance(step, FilterStep):
                layer = FilterLayer(graph=self.graph, step=step, prev=layer)

        layer = GoalLayer(graph=self.graph, goal=query.goal, prev=layer)

        results = []
        for result in layer:
            results.append(result)

        return SearchResults(graph=self.graph, query=query, results=results)
