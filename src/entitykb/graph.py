import time
from collections import defaultdict
from itertools import chain
from typing import Union, Dict, Generator, Iterable, Set

from . import Entity, Relationship, Tag, logger

KEY_OR_ID = Union[str, float]
ER = Union[Entity, Relationship]
RelationshipGenerator = Generator[Relationship, None, None]


class Graph(object):
    def __init__(self):
        self.key_or_id_to_entity: Dict[KEY_OR_ID, Entity] = dict()
        self.entity_to_id: Dict[Entity, float] = dict()
        self.out_relationships = defaultdict(set)
        self.in_relationships = defaultdict(set)

    def __repr__(self):
        return f"<Graph: ({len(self)} entities)>"

    def __len__(self):
        return len(self.entity_to_id)

    @property
    def q(self) -> "Query":
        return Query(self)

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
        self.key_or_id_to_entity[entity_id] = entity
        self.key_or_id_to_entity[entity.key] = entity
        return entity_id

    def get_entity(self, key_or_id: KEY_OR_ID):
        return self.key_or_id_to_entity.get(key_or_id)

    def get_entity_id(self, entity: Entity):
        return self.entity_to_id.get(entity)

    def add_relationship(self, rel: Relationship):
        self.out_relationships[rel.entity_a].add(rel)
        self.in_relationships[rel.entity_b].add(rel)

    def gen_in_relationships(self, entity: Entity) -> RelationshipGenerator:
        yield from self.in_relationships.get(entity, ())


class TagFilter(object):
    def __init__(self, tag: Tag):
        self.tag = tag

    def __call__(self, relationship: Relationship):
        ok = self.tag == relationship.tag
        return ok


class EntityFilter(object):
    def __init__(self, others: Iterable[Entity]):
        if others is None:
            self.others = None
            self.is_origin = True
        else:
            self.others = set(others)
            self.is_origin = False

    def __call__(self, entity: Entity):
        ok = self.is_origin or (entity in self.others)
        return ok


class InGenerator(object):
    def __init__(
        self,
        graph: Graph,
        entities: Iterable[Entity],
        tag: Tag,
        seen: Set[Entity] = None,
    ):
        self.graph = graph
        self.entities = entities
        self.tag = tag
        self.seen = seen or set()

    def __iter__(self):
        next_round = set()

        for entity in self.entities:
            for rel in self.graph.gen_in_relationships(entity=entity):
                if rel.tag == self.tag:
                    entity = rel.entity_a

                    if entity not in self.seen:
                        self.seen.add(entity)
                        next_round.add(entity)
                        yield entity

        if next_round:
            yield from InGenerator(
                graph=self.graph,
                entities=next_round,
                tag=self.tag,
                seen=self.seen,
            )


class Query(object):
    def __init__(self, graph: Graph):
        self.graph = graph
        self.tag = None
        self.batches = []

    def __getattr__(self, tag_name: str):
        self.tag = Tag.convert(tag_name)
        return self

    def __call__(self, *args):
        in_gen = InGenerator(graph=self.graph, entities=args, tag=self.tag)
        self.batches.append(in_gen)
        return self

    def __len__(self):
        return len(self.execute())

    def __iter__(self):
        yield from self.execute()

    def execute(self):
        others = None
        for entity_it in self.batches:
            next_others = set()

            entity_filter = EntityFilter(others=others)
            entity_it = filter(entity_filter, entity_it)

            for entity in entity_it:
                next_others.add(entity)

            others = next_others

        return others
