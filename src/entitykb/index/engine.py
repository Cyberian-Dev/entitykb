from dataclasses import dataclass
from typing import Iterable

from entitykb import Q, Query
from . import Graph, Terms, HAS_LABEL, EID


@dataclass
class Engine(object):
    graph: Graph
    terms: Terms

    def search(
        self, query: Query, limit: int = None, entity_it: Iterable = None,
    ) -> Iterable[EID]:
        raise NotImplementedError


@dataclass
class DefaultEngine(Engine):
    def search(
        self, query: Query, limit: int = None, entity_it: Iterable = None,
    ) -> Iterable[EID]:

        layer = entity_it

        for q in query:
            if layer is None:
                layer = NodeGenerator(q=q, graph=self.graph)
            else:
                layer = NodeFilter.create(q=q, graph=self.graph, child=layer)

        if layer:
            limit = -1 if limit is None else limit

            for entity_id in layer:
                if limit == 0:
                    break
                yield entity_id
                limit -= 1


@dataclass
class Layer(object):
    q: Q
    graph: Graph
    child: Iterable = None


@dataclass
class NodeGenerator(Layer):
    def __iter__(self):
        self.seen = set()
        for entity_id in self.iter_related_entities():
            if entity_id not in self.seen:
                self.seen.add(entity_id)
                yield entity_id

    def iter_related_entities(self):
        yield from self.iter_label_related_entities()
        yield from self.iter_tag_related_entities(self.q.others, self.q.hops)

    def iter_label_related_entities(self):
        for label in self.q.labels or ():
            yield from self.graph.get_relationships(HAS_LABEL, True, label)

    def iter_tag_related_entities(self, others, hops):
        next_round = set()

        for tag in self.q.tags or ():
            for other in others:
                other_id = self.graph.get_entity_id(other)
                entity_it = self.graph.get_relationships(
                    tag, self.q.incoming, other_id
                )
                for entity_id in entity_it:
                    if entity_id not in self.seen:
                        yield entity_id
                        next_round.add(entity_id)

        hops = hops - 1
        if next_round and hops != 0:
            yield from self.iter_tag_related_entities(next_round, hops)


@dataclass
class NodeFilter(Layer):
    def is_valid(self, entity):
        raise NotImplementedError

    def __iter__(self):
        for entity in self.child:
            if self.is_valid(entity):
                yield entity

    @classmethod
    def create(cls, q: Q, **kwargs):
        if q.labels:
            klass = LabelFilter
        else:
            klass = RelationshipFilter

        return klass(q=q, **kwargs)


@dataclass
class RelationshipFilter(NodeFilter):
    def __post_init__(self):
        ng = NodeGenerator(q=self.q, graph=self.graph)
        self.other_entity_ids = set(ng)

    def is_valid(self, entity):
        entity_id = self.graph.get_entity_id(entity)
        return entity_id in self.other_entity_ids


@dataclass
class LabelFilter(NodeFilter):
    def __post_init__(self):
        self.entity_id_sets = []
        for label in self.q.labels:
            entity_ids = self.graph.get_relationships(HAS_LABEL, True, label)
            self.entity_id_sets.append(entity_ids)

    def is_valid(self, entity):
        entity_id = self.graph.get_entity_id(entity)
        for entity_ids in self.entity_id_sets:
            if entity_id in entity_ids:
                return True
        return False
