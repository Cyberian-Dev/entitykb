from itertools import chain
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Union, Set

from entitykb import Tag, EntityValue
from entitykb.utils import ensure_iterable
from . import EID, AND, Graph, Terms


class Filter(object):
    def evaluate(self, graph: Graph, entity_id: EID):
        raise NotImplementedError

    @classmethod
    def create(cls, **data: dict):
        if data.keys() == {"label"}:
            return LabelFilter(**data)
        elif {"entities", "tags", "incoming"}.issuperset(data.keys()):
            return RelationshipFilter(**data)

    def dict(self):
        raise NotImplementedError


@dataclass
class LabelFilter(Filter):
    label: Set[str] = field(default_factory=set)

    def __post_init__(self):
        self.label = set(ensure_iterable(self.label))

    def evaluate(self, graph: Graph, entity_id: EID):
        entity = graph.get_entity(entity_id)
        return entity and (entity.label in self.label)

    def dict(self):
        return dict(label=self.label)


@dataclass
class RelationshipFilter(Filter):
    entities: Set[str]
    tags: Set[str]
    incoming: bool = True
    self_ok: bool = False
    _others: Set[EID] = None

    def __repr__(self):
        msg = f"tags={self.tags}, entities={self.entities}"
        return f"<RelationshipFilter: ({msg})>"

    def __post_init__(self):
        self.entities = set(ensure_iterable(self.entities))
        self.tags = set((tag.upper() for tag in ensure_iterable(self.tags)))

    def descend(self, graph, entities):
        others_it = graph.iterate_all_relationships(
            tags=self.tags, incoming=self.incoming, entities=entities
        )

        new_ids = set()
        for other_id, tag in others_it:
            new_ids.add(other_id)

        next_work = new_ids - self._others
        self._others.update(new_ids)

        if next_work:
            self.descend(graph, next_work)

    def find_others(self, graph: Graph):
        if self._others is None:
            self._others = set()
            self.descend(graph, self.entities)

            if self.self_ok:
                for entity in self.entities:
                    self._others.add(graph.get_entity_id(entity))

        return self._others

    def evaluate(self, graph: Graph, entity_id: EID):
        others = self.find_others(graph)
        entity_id = graph.get_entity_id(entity_id)
        result = entity_id in others
        return result

    def dict(self):
        return dict(
            tags=sorted(self.tags),
            incoming=self.incoming,
            entities=sorted(self.entities),
        )


@dataclass
class QueryStart(object):
    entities: Iterable[EntityValue] = None
    prefix: str = None
    term: str = None

    def get_iterator(self, graph: Graph, terms: Terms):
        if self.entities:
            yield from chain(self.entities)
        elif self.prefix:
            yield from terms.values(self.prefix)
        elif self.term:
            yield from terms.get(self.term)
        else:
            yield from graph

    def dict(self):
        if self.entities:
            self.entities = list(self.entities)
        data = dict(entities=self.entities, prefix=self.prefix, term=self.term)
        data = dict((k, v) for (k, v) in data.items() if v)
        return data


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

    def __len__(self):
        return len(self.filters)

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
        data = {"filters": [filter.dict() for filter in self.filters]}
        if self.join_type != "AND":
            data["join_type"] = self.join_type
        if self.exclude:
            data["exclude"] = self.exclude
        return data


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
        if self.limit is not None:
            return dict(limit=self.limit)
        else:
            return {}


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
        start = QueryStart(**data.get("start", {}))
        steps = [Step.create(**step) for step in data.get("steps", [])]
        goal = QueryGoal(**data.get("goal", {}))
        return Query(start=start, steps=steps, goal=goal)
