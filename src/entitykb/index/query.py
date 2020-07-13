from dataclasses import dataclass, field
from typing import Iterable, List, Dict, Optional, Union, Set

from entitykb import Tag

from .graph import Graph
from .const import ENTITY_VAL, EID


@dataclass
class QueryStart(object):
    entities: Iterable[ENTITY_VAL]

    def __post_init__(self):
        self.entities = list(self.entities)

    def dict(self):
        return dict(entities=self.entities)


@dataclass
class Step(object):
    @classmethod
    def create(cls, **data: dict) -> Union["FilterStep", "WalkStep"]:
        if data.keys() == {"tags", "incoming", "max_hops"}:
            return WalkStep(**data)
        else:
            return FilterStep(**data)

    def dict(self):
        raise NotImplementedError


@dataclass
class FilterStep(Step):
    include: bool = True

    def dict(self):
        return dict(include=self.include)


@dataclass
class WalkStep(Step):
    tags: Set[str]
    incoming: bool = True
    max_hops: Optional[int] = None

    def __post_init__(self):
        tags = set(Tag.convert(tag) for tag in self.tags)
        self.tags = tags or {None}

    def dict(self):
        return dict(
            tags=sorted(self.tags),
            incoming=self.incoming,
            max_hops=self.max_hops,
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


class QueryBuilder(object):
    def __init__(self, *entities: str):
        start = QueryStart(entities=entities)
        self.query = Query(start=start)

    # steps (returns self)

    def walk(self, *tags: str, incoming: bool = True, max_hops: int = None):
        walk = WalkStep(tags=tags, incoming=incoming, max_hops=max_hops,)
        self.query.steps.append(walk)
        return self

    def filter(self, **kwargs):
        q_include = FilterStep(include=True, **kwargs)
        self.query.steps.append(q_include)
        return self

    def exclude(self, **kwargs):
        q_exclude = FilterStep(include=False, **kwargs)
        self.query.steps.append(q_exclude)
        return self

    # goals (return query)

    def all(self):
        self.query.goal = QueryGoal()
        return self.query

    def first(self):
        self.query.goal = QueryGoal(limit=1)
        return self.query


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
        return f"<Result: {self.start} - {len(self.hops)} -> {self.end}>"

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

    def add_hop(self, hop):
        self.hops.append(hop)
        self.by_end_id[hop.end_id] = hop

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

    def __len__(self):
        return len(self.results)

    def dict(self):
        results = [result.dict() for result in self.results]
        return dict(query=self.query.dict(), results=results)


QB = QueryBuilder

# todo: is Q a "FilterStep" or "FilterBuilder" (not yet implemented) to build
# todo: FilterBuilder builds out a set of SubFilters for FilterStep w/ join
Q = None
