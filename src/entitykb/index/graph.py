import time
from collections import defaultdict
from itertools import chain
from typing import Union, Dict, Generator, Iterable, Set

from entitykb import (
    DocEntity,
    Entity,
    Relationship,
    ER,
    Tag,
    QueryType,
    Query,
    Q,
    logger,
    utils,
)

ENTITY_VAL = Union[Entity, DocEntity, str, float]
HAS_LABEL = "HAS_LABEL"
RelationshipGenerator = Generator[Relationship, None, None]


def generate_new_id():
    new_id = time.time()
    time.sleep(0.0)
    return new_id


class Graph(object):
    def __init__(self):
        self.entity_by_id: Dict[float, Entity] = dict()
        self.entity_key_to_id: Dict[str, float] = defaultdict(generate_new_id)
        self.relationships = {}

    def __repr__(self):
        return f"<Graph: ({len(self)} entities)>"

    def __len__(self):
        return len(self.entity_by_id)

    def __call__(self, query: QueryType):
        return self.find(query)

    def __getitem__(self, item):
        if isinstance(item, Entity):
            return self.get_entity_id(item)
        else:
            return self.get_entity(item)

    def get_entity(self, val: ENTITY_VAL):
        if isinstance(val, float):
            return self.entity_by_id.get(val)
        if isinstance(val, str):
            entity_id = self.entity_key_to_id.get(val)
            return self.entity_by_id.get(entity_id)
        if isinstance(val, DocEntity):
            return val.entity
        if isinstance(val, Entity):
            return val

    def get_entity_id(self, val: ENTITY_VAL):
        if isinstance(val, Entity):
            return self.entity_key_to_id.get(val.key)
        if isinstance(val, DocEntity):
            return self.entity_key_to_id.get(val.entity_key)
        if isinstance(val, str):
            return self.entity_key_to_id.get(val)
        if isinstance(val, float):
            return val

    def add(self, *items: ER):
        for item in chain(*items):
            if isinstance(item, Entity):
                self.add_entity(item)
            elif isinstance(item, Relationship):
                self.add_relationship(item)
            else:
                logger.warning(f"Invalid type: {type(item)}: {item}")

    def add_entity(self, entity: Entity):
        entity_id = self.entity_key_to_id[entity.key]
        self.entity_by_id[entity_id] = entity
        label_id = self.entity_key_to_id[entity.label]
        self.add_rel_using_ids(entity_id, HAS_LABEL, label_id)
        return entity_id

    def add_relationship(self, rel: Relationship):
        id_a = self.get_entity_id(rel.entity_a)
        id_b = self.get_entity_id(rel.entity_b)
        self.add_rel_using_ids(id_a, rel.tag, id_b)

    def add_rel_using_ids(self, id_a: float, tag: str, id_b: float):
        assert id_a and id_b and tag, f"Invalid: {id_a}, {tag}, {id_b}"

        top = self.relationships.setdefault(tag, {})

        rel_in = top.setdefault(False, {})
        rel_in.setdefault(id_a, set()).add(id_b)

        rel_out = top.setdefault(True, {})
        rel_out.setdefault(id_b, set()).add(id_a)

    def find(self, query: QueryType):
        query = Query.convert(query)

        entity_ids = None

        for q in query:
            if q.labels:
                labels_filter = LabelsFilter(graph=self, labels=q.labels)
                entity_it = filter(labels_filter, entity_ids)
            else:
                entity_it = NodeGenerator(graph=self, q=q)

                if entity_ids is not None:
                    entity_filter = EntityFilter(entity_ids=entity_ids)
                    entity_it = filter(entity_filter, entity_it)

            next_entity_ids = set()

            for entity_id in entity_it:
                next_entity_ids.add(entity_id)

            entity_ids = next_entity_ids

        return [self.get_entity(val) for val in entity_ids]


class LabelsFilter(object):
    def __init__(self, graph: Graph, labels: frozenset):
        self.graph = graph
        self.labels = labels

    def __call__(self, entity_id: float):
        entity = self.graph.get_entity(entity_id)
        return entity.label in self.labels


class EntityFilter(object):
    def __init__(self, entity_ids: Iterable[float]):
        self.entity_ids = set(entity_ids)

    def __call__(self, entity_id: float):
        return entity_id in self.entity_ids


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
        q = utils.first_nn(q, NodeGenerator.EMPTY_Q)

        self.graph = graph
        self.tags = utils.first_nn(tags, q.tags)
        self.starts = utils.first_nn(starts, q.entities)
        self.seen = utils.first_nn(seen, set)
        self.hops = utils.first_nn(hops, q.hops)
        self.incoming = utils.first_nn(incoming, q.incoming)

    def __iter__(self):
        next_round = set()

        for e0 in self.starts:
            e0 = self.graph.get_entity_id(e0)

            if self.tags:
                for tag in self.tags:
                    curr = self.graph.relationships.setdefault(tag, None)
                    curr = curr and curr.setdefault(self.incoming, None)
                    curr = curr and curr.setdefault(e0, None)
                    for e1 in curr or ():
                        if e1 and e1 not in self.seen:
                            self.seen.add(e1)
                            next_round.add(e1)
                            yield e1
            else:
                yield e0

        next_hops = self.hops - 1

        if next_round and next_hops != 0:
            yield from NodeGenerator(
                graph=self.graph,
                tags=self.tags,
                starts=next_round,
                seen=self.seen,
                incoming=self.incoming,
                hops=next_hops,
            )
