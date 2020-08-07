import time
from collections import defaultdict
from typing import Dict, Set, Union, Iterator, Tuple, Iterable

from entitykb import (
    DocEntity,
    Entity,
    Relationship,
    EntityValue,
)
from entitykb.utils import ensure_iterable
from . import HAS_LABEL, EID


def generate_new_id():
    new_id = time.time()
    time.sleep(0.000001)
    return new_id


class Graph(object):
    def __init__(self):
        self.entity_by_id: Dict[float, Entity] = dict()
        self.entity_key_to_id: Dict[str, float] = defaultdict(generate_new_id)
        self.rel_by_tag = {}
        self.rel_by_eid = {}

    def __repr__(self):
        return f"<Graph: ({len(self)} entities)>"

    def __len__(self):
        return len(self.entity_by_id)

    def __getitem__(self, item):
        value = self.get(item)
        if value:
            return value
        else:
            raise KeyError(f"{item} not found.")

    def __iter__(self):
        yield from self.entity_by_id.keys()

    def info(self):
        return {"entity_count": len(self.entity_by_id)}

    def get_data(self):
        return self

    def put_data(self, core: "Graph"):
        self.entity_by_id = core.entity_by_id
        self.entity_key_to_id = core.entity_key_to_id
        self.rel_by_tag = core.rel_by_tag
        self.rel_by_eid = core.rel_by_eid

    def reset_data(self):
        self.entity_by_id = dict()
        self.entity_key_to_id = defaultdict(generate_new_id)
        self.rel_by_tag = {}
        self.rel_by_eid = {}

    def get(self, item):
        if isinstance(item, Entity):
            return self.get_entity_id(item)
        else:
            return self.get_entity(item)

    def get_entity(self, val: EntityValue):
        if isinstance(val, float):
            return self.entity_by_id.get(val)
        if isinstance(val, str):
            entity_id = self.entity_key_to_id.get(val)
            return self.entity_by_id.get(entity_id)
        if isinstance(val, DocEntity):
            return val.entity
        if isinstance(val, Entity):
            return val

    def get_entity_key(self, val: EntityValue):
        entity = self.get_entity(val)
        if entity:
            return entity.key

    def get_entity_id(self, val: EntityValue):
        if isinstance(val, Entity):
            return self.entity_key_to_id.get(val.key)
        if isinstance(val, DocEntity):
            return self.entity_key_to_id.get(val.entity_key)
        if isinstance(val, str):
            return self.entity_key_to_id.get(val)
        if isinstance(val, float):
            return val

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

        # tag first
        by_tag = self.rel_by_tag.setdefault(tag, {})
        rel_in = by_tag.setdefault(False, {})
        rel_in.setdefault(id_a, set()).add(id_b)

        rel_out = by_tag.setdefault(True, {})
        rel_out.setdefault(id_b, set()).add(id_a)

        # entity first
        by_ent_a = self.rel_by_eid.setdefault(id_a, {})
        by_ent_a = by_ent_a.setdefault(False, {})
        by_ent_a.setdefault(tag, set()).add(id_b)

        by_ent_b = self.rel_by_eid.setdefault(id_b, {})
        by_ent_b = by_ent_b.setdefault(True, {})
        by_ent_b.setdefault(tag, set()).add(id_a)

    def iterate_all_relationships(
        self,
        *,
        tags: Iterable[str] = (None,),
        incoming: Iterable[bool] = (True, False),
        entities: Iterable[EntityValue] = (None,),
    ) -> Iterator[Tuple[EID, str]]:

        if incoming is None:
            incoming = (True, False)

        for tag in ensure_iterable(tags):
            for direction in ensure_iterable(incoming):
                for entity in ensure_iterable(entities):
                    yield from self.iterate_relationships(
                        tag, direction, entity
                    )

    def iterate_relationships(
        self, tag, direction, entity
    ) -> Iterator[Tuple[EID, str]]:
        eid = self.get_entity_id(entity)

        if tag:
            other_by_eid = self.rel_by_tag.get(tag, {}).get(direction, {})

            if eid:
                other_ids = other_by_eid.get(eid, ())
                yield from self.iter_other_ids(other_ids, tag)
            else:
                for other_ids in other_by_eid.values():
                    yield from self.iter_other_ids(other_ids, tag)

        elif eid:
            other_by_tag = self.rel_by_eid.get(eid, {}).get(direction, {})
            for rel_tag, other_ids in other_by_tag.items():
                if rel_tag != "HAS_LABEL":
                    yield from self.iter_other_ids(other_ids, tag)

    @classmethod
    def iter_other_ids(cls, other_ids, tag) -> Iterator[Tuple[EID, str]]:
        for other_id in other_ids:
            yield other_id, tag

    def get_relationships(
        self, tag: str, incoming: bool = None, entity: EntityValue = None
    ) -> Union[Dict, Set]:
        curr = self.rel_by_tag.get(tag)

        if curr:
            if incoming is not None:
                curr = curr.get(incoming)

                if entity is not None:
                    entity_id = self.get_entity_id(entity)
                    curr = curr.get(entity_id)

            elif entity is not None:
                entity_id = self.get_entity_id(entity)
                curr = curr.get(True, {}).get(entity_id) | curr.get(
                    False, {}
                ).get(entity_id)

        return curr or set()
