from dataclasses import dataclass, field
from typing import Iterator, Set, Dict, List

from entitykb import Entity

from . import (
    Graph,
    Query,
    QueryStart,
    QueryGoal,
    Result,
    SearchResults,
    Terms,
    WalkStep,
    FilterStep,
)


@dataclass
class Layer(object):
    graph: Graph
    terms: Terms

    def __iter__(self) -> Iterator[Result]:
        raise NotImplementedError


@dataclass
class StartLayer(Layer):
    start: QueryStart

    def __iter__(self) -> Iterator[Result]:
        entity_id_it = self.start.get_iterator(self.graph, self.terms)
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

        if result.end_id is not None:
            for req_tag in self.step.tags:
                others_it = self.graph.iterate_all_relationships(
                    tags=req_tag,
                    incoming=self.step.incoming,
                    entities=result.end_id,
                )

                for (end_id, rel_tag) in others_it:
                    next_result = result.push(tag=rel_tag, end_id=end_id)
                    if next_result not in self.seen:
                        self.seen.add(next_result)
                        children.add(next_result)
                        if self.step.max_hops is None or (
                            len(next_result.hops) < self.step.max_hops
                        ):
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

    def __iter__(self) -> Iterator[Result]:
        for result in self.prev:
            if self.step.evaluate(self.graph, result.end_id):
                yield result


@dataclass
class GoalLayer(Layer):
    goal: QueryGoal
    prev: Layer

    def __iter__(self) -> Iterator[Result]:
        count = 0

        for result in self.prev:
            if self.goal.limit is not None and count >= self.goal.limit:
                break

            yield result
            count += 1


@dataclass
class Searcher(object):
    graph: Graph
    terms: Terms

    def __call__(self, query: Query):
        return self.search(query)

    def search(self, query: Query) -> SearchResults:
        """
        Execute search using Query object.
        """
        layer = StartLayer(
            graph=self.graph, terms=self.terms, start=query.start
        )

        for step in query.steps:
            if isinstance(step, WalkStep):
                layer = WalkLayer(
                    graph=self.graph, terms=self.terms, step=step, prev=layer
                )
            elif isinstance(step, FilterStep):
                layer = FilterLayer(
                    graph=self.graph, terms=self.terms, step=step, prev=layer
                )

        layer = GoalLayer(
            graph=self.graph, terms=self.terms, goal=query.goal, prev=layer
        )

        results = []
        for result in layer:
            results.append(result)

        return SearchResults(graph=self.graph, query=query, results=results)

    def most_relevant(self, query: Query) -> Entity:
        """
        Returns the entity with the most results.
        Tie-breaker is the entity with the least number of hops.
        """
        rollup = self.rollup(query)

        if not rollup:
            return

        if len(rollup) == 1:
            return next(iter(rollup.keys()))

        aggregates = []

        for entity, results in rollup.items():
            agg = (-len(results), min(len(r.hops) for r in results), entity)
            aggregates.append(agg)

        aggregates = sorted(aggregates)
        _, _, entity = aggregates[0]
        return entity

    def closest(self, query: Query) -> Entity:
        """
        Returns the entity with the least number of hops.
        Tie-breaker is the entity with the most results.
        """
        rollup = self.rollup(query)

        if not rollup:
            return

        if len(rollup) == 1:
            return next(iter(rollup.keys()))

        aggregates = []

        for entity, results in rollup.items():
            agg = (min(len(r.hops) for r in results), -len(results), entity)
            aggregates.append(agg)

        _, _, entity = sorted(aggregates)[0]
        return entity

    def rollup(self, query: Query) -> Dict[Entity, List[Result]]:
        """
        Roll-up search results by Entity and return dictionary.
        """
        results = self.search(query)
        rollup = {}

        for result in results:
            rollup.setdefault(result.entity, []).append(result)

        return rollup
