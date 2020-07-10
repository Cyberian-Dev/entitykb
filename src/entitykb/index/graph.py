import time
from collections import defaultdict
from itertools import chain
from typing import Dict, Set, Union

from entitykb import (
    DocEntity,
    Entity,
    Relationship,
    ER,
    logger,
)
from . import HAS_LABEL, ENTITY_VAL


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

    def __getitem__(self, item):
        value = self.get(item)
        if value:
            return value
        else:
            raise KeyError(f"{item} not found.")

    def get_data(self):
        return self

    def put_data(self, core: "Graph"):
        self.entity_by_id = core.entity_by_id
        self.entity_key_to_id = core.entity_key_to_id
        self.relationships = core.relationships

    def reset_data(self):
        self.entity_by_id = None
        self.entity_key_to_id = None
        self.relationships = None

    def get(self, item):
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

    def get_relationships(
        self, tag: str, incoming: bool = None, entity: ENTITY_VAL = None
    ) -> Union[Dict, Set]:
        curr = self.relationships.get(tag)

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
