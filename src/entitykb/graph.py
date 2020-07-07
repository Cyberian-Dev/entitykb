import enum
import time
from collections import defaultdict
from itertools import chain

from typing import Union, Dict, Set, Generator, List

from . import Entity, Relationship, Tag, logger, Label

ER = Union[Entity, Relationship]

IS_A = Tag.IS_A
CONTAINS = Tag.CONTAINS


class Direction(enum.Enum):
    IN = "IN"
    OUT = "OUT"
    BOTH = "BOTH"


class Graph(object):
    def __init__(self):
        self.id_to_entity: Dict[float, Entity] = dict()
        self.entity_to_id: Dict[Entity, float] = dict()
        self.out_relationships = defaultdict(set)
        self.in_relationships = defaultdict(set)

    def __repr__(self):
        n0 = f"{self.num_entities} entities"
        n1 = f"{self.num_relationships} relationships"
        return f"<Graph: ({n0}, {n1})>"

    @property
    def num_entities(self):
        return len(self.entity_to_id)

    @property
    def num_relationships(self):
        return len(self.out_relationships)

    def q(self, *args) -> "Query":
        return Query(self, *args)

    def add(self, *items: ER):
        for item in chain(items):
            if isinstance(item, Entity):
                self.add_entity(item)
            elif isinstance(item, Relationship):
                self.add_relationship(item)
            else:
                logger.warning(f"Invalid type: {type(item)}: {item}")

    def add_entity(self, entity: Entity):
        entity_id = self.entity_to_id.setdefault(entity, time.time())
        self.id_to_entity[entity_id] = entity
        return entity_id

    def get_entity(self, entity_id: float):
        return self.id_to_entity.get(entity_id)

    def get_entity_id(self, entity: Entity):
        return self.entity_to_id.get(entity)

    def add_relationship(self, rel: Relationship):
        self.out_relationships[rel.entity_a].add(rel)
        self.in_relationships[rel.entity_b].add(rel)

    def iterate_relationships(
        self, entity: Entity, direction: Direction
    ) -> Generator[Relationship, None, None]:
        direction = direction or Direction.OUT

        if direction in {Direction.OUT, Direction.BOTH}:
            yield from self.out_relationships.get(entity, ())

        if direction in {Direction.IN, Direction.BOTH}:
            yield from self.in_relationships.get(entity, ())


class TagFilter(object):
    def __init__(self, tags: Set[Tag]):
        self.tags = tags
        self.no_tags = len(tags) == 1

    def __call__(self, relationship: Relationship):
        ok = self.no_tags or relationship.tag in self.tags
        return ok


class EntityFilter(object):
    def __init__(self, entity: Entity, others: List[Entity]):
        self.entity = entity
        self.others = set(others)
        self.no_others = len(self.others)

    def __call__(self, rel: Relationship):
        ok = self.no_others or (rel.other(entity=self.entity) in self.others)
        return ok


class Query(object):
    def __init__(self, *args):
        self.graphs = []
        self.entities = []
        self.relationships = []
        self.tags = set()
        self.directions = set()
        self.labels = []
        self.separate_args(*args)

    def __getattr__(self, tag_name: str):
        tag = Tag.convert(tag_name)
        self.separate_args(tag)
        return self

    def __call__(self, *args):
        self.separate_args(*args)
        return self.execute()

    def __len__(self):
        return len(self.execute())

    def get_direction(self) -> Direction:
        if len(self.directions) == 0:
            return Direction.OUT
        elif len(self.directions) == 1:
            return next(iter(self.directions))
        else:
            return Direction.BOTH

    def execute(self):
        direction = self.get_direction()
        result = ()

        for graph in self.graphs:
            if self.entities:
                entity, others = self.entities[0], self.entities[1:]
                rel_it = graph.iterate_relationships(entity, direction)
                rel_it = filter(TagFilter(self.tags), rel_it)
                rel_it = filter(EntityFilter(entity, others), rel_it)
                result = set(rel_it)

        return result

    def separate_args(self, *args):
        for arg in args:
            if isinstance(arg, Graph):
                self.graphs.append(arg)

            elif isinstance(arg, Entity):
                self.entities.append(arg)

            elif isinstance(arg, Relationship):
                self.relationships.append(arg)

            elif isinstance(arg, (str, Tag)):
                self.tags.add(Tag.convert(arg))

            elif isinstance(arg, Direction):
                self.directions.add(arg)

            elif isinstance(arg, Label):
                self.labels.append(arg)

            else:
                logger.warning(f"Unknown argument to query: {arg}")
