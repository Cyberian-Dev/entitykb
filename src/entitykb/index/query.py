from itertools import chain
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Union, Set

from entitykb import Tag, EntityValue
from . import EID, AND, Graph


class Filter(object):
    def evaluate(self, graph: Graph, entity_id: EID):
        raise NotImplementedError

    @classmethod
    def create(cls, **data: dict):
        if data.keys() == {"labels"}:
            return LabelFilter(**data)

    def dict(self):
        raise NotImplementedError


@dataclass
class LabelFilter(Filter):
    labels: Set[str] = field(default_factory=set)

    def evaluate(self, graph: Graph, entity_id: EID):
        entity = graph.get_entity(entity_id)
        return entity and (entity.label in self.labels)

    def dict(self):
        return dict(labels=self.labels)


@dataclass
class RelationshipFilter(Filter):
    tags: Set[str]
    incoming: bool = True
    max_hops: Optional[int] = None
    passthru: bool = False

    def evaluate(self, graph: Graph, entity_id: EID):
        entity = graph.get_entity(entity_id)
        return entity.label in self.labels

    def dict(self):
        return dict(
            tags=sorted(self.tags),
            incoming=self.incoming,
            max_hops=self.max_hops,
            passthru=self.passthru,
        )


@dataclass
class QueryStart(object):
    entities: Iterable[EntityValue] = None
    iterables: Iterable[Iterable[EntityValue]] = None

    def get_iterator(self, graph: Graph):
        if self.entities:
            yield from self.entities
        elif self.iterables is not None:
            yield from chain(self.iterables)
        else:
            yield from graph

    def dict(self):
        # todo: how to handle terms query starts?
        self.entities = list(self.entities)
        return dict(entities=self.entities)


@dataclass
class Step(object):
    @classmethod
    def create(cls, **data: dict) -> Union["FilterStep", "WalkStep"]:
        if data.keys() == {"tags", "incoming", "max_hops", "passthru"}:
            return WalkStep(**data)
        else:
            data["filters"] = [
                Filter.create(**f) for f in data.get("filters", [])
            ]
            return FilterStep(**data)

    def dict(self):
        raise NotImplementedError


@dataclass
class FilterStep(Step):
    filters: List[Filter]
    join_type: str = AND
    exclude: bool = False

    def evaluate(self, graph: Graph, entity_id: EID):
        success = self.join_type == AND
        for filter in self.filters:
            if self.join_type == AND:
                success = success and filter.evaluate(graph, entity_id)
            else:
                success = success or filter.evaluate(graph, entity_id)

        if self.exclude:
            success = not success

        return success

    def dict(self):
        filters = [filter.dict() for filter in self.filters]
        return dict(
            filters=filters, join_type=self.join_type, exclude=self.exclude
        )


@dataclass
class WalkStep(Step):
    tags: Set[str]
    incoming: bool = True
    max_hops: Optional[int] = None
    passthru: bool = False

    def __post_init__(self):
        tags = set(Tag.convert(tag) for tag in self.tags)
        self.tags = tags or {None}

    def dict(self):
        return dict(
            tags=sorted(self.tags),
            incoming=self.incoming,
            max_hops=self.max_hops,
            passthru=self.passthru,
        )


@dataclass
class QueryGoal(object):
    limit: int = None

    def dict(self):
        return dict(limit=self.limit)


@dataclass
class Query(object):
    start: QueryStart
    steps: List[Step] = field(default_factory=list)
    goal: QueryGoal = None

    def dict(self):
        return dict(
            start=self.start.dict(),
            steps=[step.dict() for step in self.steps],
            goal=self.goal.dict(),
        )

    @classmethod
    def from_dict(cls, data: dict):
        start = QueryStart(**data.get("start"))
        steps = [Step.create(**step) for step in data.get("steps", [])]
        goal = QueryGoal(**data.get("goal"))
        return Query(start=start, steps=steps, goal=goal)
