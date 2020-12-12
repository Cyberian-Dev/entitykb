from dataclasses import dataclass, field
from typing import Iterable, Iterator, Set

from entitykb import (
    FieldCriteria,
    FilterStep,
    Graph,
    Node,
    Traversal,
    EdgeCriteria,
    Trail,
    WalkStep,
    under_limit,
)


@dataclass
class Layer(object):
    graph: Graph

    def __iter__(self) -> Iterator[Trail]:
        raise NotImplementedError


@dataclass
class StartLayer(Layer):
    starts: Iterable

    def __iter__(self) -> Iterator[Trail]:
        seen = set()
        for start in self.starts:
            start = Node.to_key(start)
            if start not in seen:
                seen.add(start)
                yield Trail(start=start)


@dataclass
class WalkLayer(Layer):
    step: WalkStep
    prev: Layer
    seen: Set = field(default_factory=set)

    def descend(self, trail: Trail):
        children = set()

        if trail.end is not None:
            others_it = self.graph.iterate_edges(
                verbs=self.step.verbs,
                directions=self.step.directions,
                nodes=trail.end,
            )

            for (end, edge) in others_it:
                next_trail = trail.push(end=end, edge=edge)
                if next_trail not in self.seen:
                    self.seen.add(next_trail)
                    children.add(next_trail)

                    if under_limit(next_trail.hops, self.step.max_hops):
                        yield from self.descend(next_trail)

        # yield last, handle case of parallel rel w/ multiple verbs
        yield from children

    def __iter__(self) -> Iterator[Trail]:
        for trail in self.prev:
            if self.step.passthru:
                yield trail

            self.seen.add(trail)

            yield from self.descend(trail)


@dataclass
class FilterLayer(Layer):
    step: FilterStep
    prev: Layer

    def evaluate_attr_criteria(self, criteria, trail: Trail):
        node = self.graph.get_node(trail.end)
        try:
            other = getattr(node, criteria.field)
            return criteria.do_compare(other)
        except AttributeError:
            return False

    def evaluate_rel_criteria(self, criteria, trail: Trail):
        it = self.graph.iterate_edges(
            verbs=criteria.verbs,
            directions=criteria.directions,
            nodes=trail.end,
        )

        node_set = set(criteria.keys)

        found = False
        for (key, edge) in it:
            if key in node_set:
                found = True
                break

        return found

    def evaluate_criteria(self, criteria, trail: Trail):
        if isinstance(criteria, FieldCriteria):
            return self.evaluate_attr_criteria(criteria, trail)

        if isinstance(criteria, EdgeCriteria):
            return self.evaluate_rel_criteria(criteria, trail)

        raise NotImplementedError(f"Unknown Criteria: {criteria}")

    def evaluate(self, trail: Trail):
        success = self.step.all

        for criteria in self.step.criteria:
            if self.step.all:
                success = success and self.evaluate_criteria(criteria, trail)
            else:
                success = success or self.evaluate_criteria(criteria, trail)

        if self.step.exclude:
            success = not success

        return success

    def __iter__(self) -> Iterator[Trail]:
        for trail in self.prev:
            if self.evaluate(trail):
                yield trail


@dataclass
class Searcher(object):
    graph: Graph
    starts: Iterable
    traversal: Traversal
    layer: Layer = None

    def __iter__(self):
        self.layer = self.initialize()
        for trail in self.layer:
            yield trail

    def initialize(self) -> Layer:
        raise NotImplementedError


class DefaultSearcher(Searcher):
    def initialize(self) -> Layer:
        layer = StartLayer(self.graph, starts=self.starts)

        for step in self.traversal or []:
            if isinstance(step, WalkStep):
                layer = WalkLayer(graph=self.graph, step=step, prev=layer)
            elif isinstance(step, FilterStep):
                layer = FilterLayer(graph=self.graph, step=step, prev=layer)

        return layer
