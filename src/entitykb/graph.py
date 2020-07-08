import time
from collections import defaultdict
from itertools import chain
from typing import Union, Dict, Generator, Iterable, Set

from . import Entity, Relationship, Tag, QueryType, Query, Q, logger

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

    def __call__(self, query: QueryType):
        return self.find(query)

    def add(self, *items: ER):
        for item in chain(*items):
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

    def rel_it(self, entity: Entity, incoming: bool) -> RelationshipGenerator:
        if incoming:
            yield from self.in_relationships.get(entity, ())
        else:
            yield from self.out_relationships.get(entity, ())

    def find(self, query: QueryType):
        query = Query.convert(query)

        entities = None

        for q in query:
            entity_filter = EntityFilter(entities=entities)
            entity_it = NodeGenerator(graph=self, q=q)
            entity_it = filter(entity_filter, entity_it)

            next_entities = set()

            for entity in entity_it:
                next_entities.add(entity)

            entities = next_entities

        return entities


class TagFilter(object):
    def __init__(self, tag: Tag):
        self.tag = tag

    def __call__(self, relationship: Relationship):
        ok = self.tag == relationship.tag
        return ok


class EntityFilter(object):
    def __init__(self, entities: Iterable[Entity]):
        if entities is None:
            self.entities = None
            self.is_origin = True
        else:
            self.entities = set(entities)
            self.is_origin = False

    def __call__(self, entity: Entity):
        ok = self.is_origin or (entity in self.entities)
        return ok


def first_nn(*items):
    """ Returns first not none argument. """
    for item in items:
        if item is not None:
            if item in {list, set, tuple, dict}:
                return item()
            else:
                return item


class NodeGenerator(object):

    EMPTY_Q = Q()

    def __init__(
        self,
        graph: Graph,
        q: Q = None,
        tags: Set[Tag] = None,
        starts: Set[Entity] = None,
        seen: Set[Entity] = None,
        incoming: bool = None,
        hops: int = None,
    ):
        q = first_nn(q, NodeGenerator.EMPTY_Q)

        self.graph = graph
        self.tags = first_nn(tags, q.tags)
        self.starts = first_nn(starts, q.entities)
        self.seen = first_nn(seen, set)
        self.hops = first_nn(hops, q.hops)
        self.incoming = first_nn(incoming, q.incoming)

    def __iter__(self):
        next_round = set()

        for e0 in self.starts:
            for rel in self.graph.rel_it(entity=e0, incoming=self.incoming):
                if rel.tag in self.tags:
                    e1 = rel.entity_a if self.incoming else rel.entity_b

                    if e1 not in self.seen:
                        self.seen.add(e1)
                        next_round.add(e1)
                        yield e1

        if next_round:
            yield from NodeGenerator(
                graph=self.graph,
                tags=self.tags,
                starts=next_round,
                seen=self.seen,
                incoming=self.incoming,
                hops=self.hops - 1,
            )
