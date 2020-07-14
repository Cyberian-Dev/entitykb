import time
from collections import defaultdict
from typing import Dict, Set, Union, Iterator, Tuple

from entitykb import (
    DocEntity,
    Entity,
    Relationship,
    EntityValue,
)
from . import HAS_LABEL, EID


def generate_new_id():
    new_id = time.time()
    time.sleep(0.000001)
    return new_id


class Graph(object):
    def __init__(self):
        self.entity_by_id: Dict[float, Entity] = dict()
        self.entity_key_to_id: Dict[str, float] = defaultdict(generate_new_id)
        self.relationships_by_tag = {}
        self.relationships_by_entity_id = {}

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

    def get_data(self):
        return self

    def put_data(self, core: "Graph"):
        self.entity_by_id = core.entity_by_id
        self.entity_key_to_id = core.entity_key_to_id
        self.relationships_by_tag = core.relationships_by_tag
        self.relationships_by_entity_id = core.relationships_by_entity_id

    def reset_data(self):
        self.entity_by_id = dict()
        self.entity_key_to_id = defaultdict(generate_new_id)
        self.relationships_by_tag = {}
        self.relationships_by_entity_id = {}

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
        by_tag = self.relationships_by_tag.setdefault(tag, {})
        rel_in = by_tag.setdefault(False, {})
        rel_in.setdefault(id_a, set()).add(id_b)

        rel_out = by_tag.setdefault(True, {})
        rel_out.setdefault(id_b, set()).add(id_a)

        # entity first
        by_ent_a = self.relationships_by_entity_id.setdefault(id_a, {})
        by_ent_a = by_ent_a.setdefault(False, {})
        by_ent_a.setdefault(tag, set()).add(id_b)

        by_ent_b = self.relationships_by_entity_id.setdefault(id_b, {})
        by_ent_b = by_ent_b.setdefault(True, {})
        by_ent_b.setdefault(tag, set()).add(id_a)

    def iterate_others(
        self, *, tag: str, incoming: bool, entity: EntityValue = None
    ) -> Iterator[Tuple[str, EID]]:
        entity_id = entity and self.get_entity_id(entity)
        incomings = {True, False} if incoming is None else {incoming}

        if tag:
            top = self.relationships_by_tag.get(tag)
            next_keys = (entity_id,) if entity_id else ()
        elif entity_id:
            top = self.relationships_by_entity_id.get(entity_id)
            next_keys = ()
        else:
            raise ValueError("Need to provide either a tag or entity.")

        for incoming in incomings:
            curr = top.get(incoming, {})
            next_keys = next_keys or (curr.keys() - {"HAS_LABEL"})
            for key in next_keys:
                other_ids = curr.get(key, set())
                for other_id in other_ids:
                    yield tag or key, other_id

    def get_relationships(
        self, tag: str, incoming: bool = None, entity: EntityValue = None
    ) -> Union[Dict, Set]:
        curr = self.relationships_by_tag.get(tag)

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
