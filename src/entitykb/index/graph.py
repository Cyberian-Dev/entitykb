import time
from collections import defaultdict
from itertools import count
from typing import Dict, Iterator, Tuple, Iterable

from entitykb import Node, Entity, Relationship, Resource, Label, DocEntity
from entitykb.utils import ensure_iterable
from . import HAS_LABEL


class Graph(object):
    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def info(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def put_data(self, core):
        raise NotImplementedError

    def reset_data(self):
        raise NotImplementedError

    def add_entity(self, entity: Entity):
        raise NotImplementedError

    def add_relationship(self, rel: Relationship):
        raise NotImplementedError

    def get_node_id(self, item):
        raise NotImplementedError

    def get_node(self, item):
        raise NotImplementedError

    def get_entity(self, item):
        raise NotImplementedError

    def get_key(self, item):
        raise NotImplementedError


class GraphCore(object):
    def __init__(self):
        self.key_to_id: Dict[str, float] = defaultdict(GraphCore.new_node_id)
        self.node_by_id: Dict[float, Node] = dict()
        self.edge_by_tag = {}
        self.edge_by_node = {}
        self.edge_counter = count()

    def __len__(self):
        return len(self.node_by_id)

    def __iter__(self):
        yield from self.node_by_id.keys()

    def info(self):
        return {
            "edges": self.num_edges,
            "nodes": len(self.node_by_id),
        }

    @property
    def num_edges(self):
        # https://stackoverflow.com/a/62880668
        return self.edge_counter.__reduce__()[1][0]

    @staticmethod
    def new_node_id():
        node_id = time.time()
        time.sleep(0.000001)
        return node_id

    def store_node(self, node: Node):
        node_id = self.key_to_id[node.key]
        self.node_by_id[node_id] = node
        return node_id

    def store_edge(self, id_a: float, tag: str, id_b: float):
        # tag -> outcoming -> a -> b
        by_tag = self.edge_by_tag.setdefault(tag, {})
        rel_in = by_tag.setdefault(False, {})
        rel_in.setdefault(id_a, set()).add(id_b)

        # tag -> incoming -> b -> a
        rel_out = by_tag.setdefault(True, {})
        rel_out.setdefault(id_b, set()).add(id_a)

        # a -> outcoming -> tag -> b
        by_ent_a = self.edge_by_node.setdefault(id_a, {})
        by_ent_a = by_ent_a.setdefault(False, {})
        by_ent_a.setdefault(tag, set()).add(id_b)

        # b -> incoming -> tag -> b
        by_ent_b = self.edge_by_node.setdefault(id_b, {})
        by_ent_b = by_ent_b.setdefault(True, {})
        by_ent_b.setdefault(tag, set()).add(id_a)

        # increment edge counter
        next(self.edge_counter)

    def get_node_id(self, key: str):
        return self.key_to_id.get(key)

    def get_node(self, *, key: str = None, node_id: float = None):
        node_id = node_id or self.get_node_id(key=key)
        return self.node_by_id.get(node_id)


class DefaultGraph(Graph):
    def __init__(self):
        self.core = GraphCore()

    def __repr__(self):
        return f"<Graph: {len(self.core.node_by_id)} nodes>"

    def __len__(self):
        return len(self.core)

    def __iter__(self):
        yield from self.core

    def info(self):
        return self.core.info()

    def get_data(self):
        return self.core

    def put_data(self, core: GraphCore):
        self.core = core

    def reset_data(self):
        self.core = GraphCore()

    def add_entity(self, entity: Entity):
        entity_id = self.core.store_node(entity)
        label_id = self.core.store_node(entity.label)
        self.core.store_edge(entity_id, HAS_LABEL, label_id)
        return entity_id

    def add_relationship(self, rel: Relationship):
        id_a = self.get_node_id(rel.node_a)
        id_b = self.get_node_id(rel.node_b)
        self.core.store_edge(id_a=id_a, tag=rel.tag, id_b=id_b)

    def get_node_id(self, item):
        if isinstance(item, float):
            return item
        if isinstance(item, str):
            return self.core.get_node_id(key=item)
        if isinstance(item, (Entity, Resource, Label)):
            return self.core.get_node_id(key=item.key)
        if isinstance(item, DocEntity):
            return self.core.get_node_id(key=item.entity_key)

    def get_node(self, item):
        if isinstance(item, (Entity, Resource, Label)):
            return item
        if isinstance(item, float):
            return self.core.get_node(node_id=item)
        if isinstance(item, str):
            return self.core.get_node(key=item)

    def get_entity(self, item):
        node = self.get_node(item)
        if isinstance(node, Entity):
            return node

    def get_key(self, item):
        if isinstance(item, str):
            return item

        entity = self.get_node(item)
        return entity and entity.key

    def iterate_all_relationships(
        self,
        *,
        tags: Iterable[str] = (None,),
        incoming: Iterable[bool] = (True, False),
        entities: Iterable = (None,),
    ) -> Iterator[Tuple[float, str]]:

        if incoming is None:
            incoming = (True, False)

        for tag in ensure_iterable(tags):
            for direction in ensure_iterable(incoming):
                for entity in ensure_iterable(entities):
                    yield from self._do_iter(tag, direction, entity)

    def _do_iter(self, tag, direction, entity) -> Iterator[Tuple[float, str]]:
        eid = self.get_node_id(entity)

        if tag:
            other_by_eid = self.core.edge_by_tag.get(tag, {}).get(
                direction, {}
            )

            if eid:
                other_ids = other_by_eid.get(eid, ())
                yield from self._do_iter_other(other_ids, tag)
            else:
                for other_ids in other_by_eid.values():
                    yield from self._do_iter_other(other_ids, tag)

        elif eid:
            other_by_tag = self.core.edge_by_node.get(eid, {}).get(
                direction, {}
            )
            for rel_tag, other_ids in other_by_tag.items():
                if rel_tag != HAS_LABEL:
                    yield from self._do_iter_other(other_ids, tag)

    @classmethod
    def _do_iter_other(cls, other_ids, tag) -> Iterator[Tuple[float, str]]:
        for other_id in other_ids:
            yield other_id, tag
