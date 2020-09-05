from threading import Lock

from .model import Edge, Direction, ensure_iterable


class NestedDict(dict):
    def __missing__(self, key):
        value = NestedDict()
        self[key] = value
        return value


class EdgeIndex(object):
    def __init__(self):
        self.by_node_key = NestedDict()
        self.by_edge_tag = NestedDict()
        self.count = 0
        self.lock = Lock()

    def __len__(self):
        return self.count

    def save(self, edge):
        any_add = False
        with self.lock:
            for a, dir, tag, b in self._edge_keys(edge):
                bottom = self.by_node_key[a][dir][tag]
                any_add = self._do_add(bottom, b, edge) or any_add

                bottom = self.by_edge_tag[tag][dir][a]
                any_add = self._do_add(bottom, b, edge) or any_add

            if any_add:
                self.count += 1
        return any_add

    def delete(self, edge):
        any_del = False
        with self.lock:
            for a, dir, tag, b in self._edge_keys(edge):
                keys = (a, dir, tag, b)
                any_del = self._do_delete(self.by_node_key, keys) or any_del

                keys = (tag, dir, a, b)
                any_del = self._do_delete(self.by_edge_tag, keys) or any_del

            if any_del:
                self.count -= 1
        return any_del

    def iterate(self, tags=None, directions=None, nodes=None):
        tags = (None,) if not tags else tags
        directions = tuple(Direction) if directions is None else directions
        nodes = (None,) if nodes is None else nodes

        for tag in ensure_iterable(tags):
            for direction in ensure_iterable(directions):
                for node in ensure_iterable(nodes):
                    yield from self._do_iter(tag, direction, node)

    # private methods

    @classmethod
    def _edge_keys(cls, edge: Edge):
        yield edge.start, Direction.outgoing, edge.tag, edge.end
        yield edge.end, Direction.incoming, edge.tag, edge.start

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

    def _do_iter(self, tag, direction, node):
        if tag:
            other_by_node = self.by_edge_tag.get(tag, {}).get(direction, {})

            if node:
                other_map = other_by_node.get(node, {})
                yield from self._do_iter_other(other_map)
            else:
                for other_map in other_by_node.values():
                    yield from self._do_iter_other(other_map)

        elif node:
            other_by_tag = self.by_node_key.get(node, {}).get(direction, {})
            for other_map in other_by_tag.values():
                yield from self._do_iter_other(other_map)

    @classmethod
    def _do_iter_other(cls, other_map):
        for other, edge in other_map.items():
            yield other, edge
