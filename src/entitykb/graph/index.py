from collections import defaultdict
from threading import Lock
from typing import Dict, Set

from entitykb.models import Node, Edge, Direction, ensure_iterable

lock = Lock()


class NestedDict(dict):
    def __missing__(self, key):
        value = NestedDict()
        self[key] = value
        return value


class NodeIndex(object):
    def __init__(self):
        self.nodes_by_key: Dict[str, Node] = {}
        self.nodes_by_label: Dict[str, Set[Node]] = defaultdict(set)

    def __len__(self):
        return len(self.nodes_by_key)

    def __iter__(self):
        return iter(self.nodes_by_key.values())

    def __contains__(self, key):
        return key in self.nodes_by_key

    def get(self, key: str):
        return self.nodes_by_key.get(key)

    def save(self, node: Node):
        self.nodes_by_key[node.key] = node
        self.nodes_by_label[node.label].add(node)

    def remove(self, key: str) -> Node:
        node = self.nodes_by_key.pop(key, None)
        if node:
            nodes = self.nodes_by_label[node.label]
            nodes.remove(node)
        return node

    def get_labels(self) -> Set[str]:
        return sorted(self.nodes_by_label.keys())

    def iterate_keys_by_label(self, label):
        nodes = self.nodes_by_label.get(label, [])
        for node in nodes:
            yield node.key


class EdgeIndex(object):
    def __init__(self):
        self.by_node_key = NestedDict()
        self.by_edge_verb = NestedDict()
        self.count = 0

    def __len__(self):
        return self.count

    def save(self, edge):
        any_add = False
        with lock:
            for a, dir, verb, b in self._edge_keys(edge):
                bottom = self.by_node_key[a][dir][verb]
                any_add = self._do_add(bottom, b, edge) or any_add

                bottom = self.by_edge_verb[verb][dir][a]
                any_add = self._do_add(bottom, b, edge) or any_add

            if any_add:
                self.count += 1
        return any_add

    def remove(self, edge):
        any_del = False
        with lock:
            for a, dir, verb, b in self._edge_keys(edge):
                keys = (a, dir, verb, b)
                any_del = self._do_delete(self.by_node_key, keys) or any_del

                keys = (verb, dir, a, b)
                any_del = self._do_delete(self.by_edge_verb, keys) or any_del

            if any_del:
                self.count -= 1
        return any_del

    def iterate(self, verbs=None, directions=None, nodes=None):
        verbs = (None,) if not verbs else verbs
        directions = Direction.as_tuple(directions, all_if_none=True)
        nodes = (None,) if nodes is None else nodes

        for verb in ensure_iterable(verbs):
            for direction in ensure_iterable(directions):
                for node in ensure_iterable(nodes):
                    node_key = Node.to_key(node)
                    yield from self._do_iter(verb, direction, node_key)

    def get_verbs(self) -> Set[str]:
        return sorted(self.by_edge_verb.keys())

    # private methods

    @classmethod
    def _edge_keys(cls, edge: Edge):
        yield edge.start, Direction.outgoing, edge.verb, edge.end
        yield edge.end, Direction.incoming, edge.verb, edge.start

    @classmethod
    def _do_add(cls, data, key, value):
        was_added = False
        if key not in data:
            data[key] = value
            was_added = True
        return was_added

    @classmethod
    def _do_delete(cls, data, keys):
        if len(keys) == 1:
            was_deleted = data.pop(keys[0], False) is not False

        else:
            key, others = keys[0], keys[1:]
            sub = data[key]

            # descend thru sub directory
            was_deleted = cls._do_delete(sub, others)

            # sub dictionary is now empty, remove from parent
            if len(sub) == 0:
                data.pop(key, None)

        return was_deleted

    def _do_iter(self, verb, direction, node):
        if verb:
            other_by_node = self.by_edge_verb.get(verb, {}).get(direction, {})

            if node:
                other_map = other_by_node.get(node, {})
                yield from self._do_iter_other(other_map)
            else:
                for other_map in other_by_node.values():
                    yield from self._do_iter_other(other_map)

        elif node:
            other_by_verb = self.by_node_key.get(node, {}).get(direction, {})
            for other_map in other_by_verb.values():
                yield from self._do_iter_other(other_map)

    @classmethod
    def _do_iter_other(cls, other_map):
        for other, edge in list(other_map.items()):
            yield other, edge
