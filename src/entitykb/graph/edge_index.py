from collections import defaultdict as dd
from threading import Lock
from typing import Set

from entitykb.models import Node, Edge, Direction, ensure_iterable, SmartList

lock = Lock()


class EdgeIndex(object):
    def __init__(self):
        self.by_start = {}  # start -> {verb -> out_edges}
        self.by_end = {}  # end -> {verb -> in_edges}
        self.by_verb = {}  # verb -> {start -> out_edges}

    def __len__(self):
        count = 0

        for vd in self.by_start.values():
            for e in vd.values():
                count += len(e)

        return count

    def get_verbs(self) -> Set[str]:
        return self.by_verb.keys()

    def save(self, edge: Edge):
        with lock:
            start_dict = self.by_start.setdefault(edge.start, dd(SmartList))
            start_dict[edge.verb].append(edge)

            # by_verb is same as by_start, with different key ordering
            verb_dict = self.by_verb.setdefault(edge.verb, {})
            verb_dict[edge.start] = start_dict[edge.verb]

            # by_end flips the direction of edge
            end_dict = self.by_end.setdefault(edge.end, dd(SmartList))
            end_dict[edge.verb].append(edge)

    def remove(self, edge: Edge):
        with lock:
            self._del_start_edge(edge)
            self._del_end_edge(edge)

    def _del_start_edge(self, edge):
        start_verb = self.by_start.get(edge.start)
        if start_verb is not None:
            out_edges = start_verb.get(edge.verb)
            out_edges.remove(edge)

    def _del_end_edge(self, edge):
        end_verb = self.by_end.get(edge.end)
        if end_verb is not None:
            in_edges = end_verb.get(edge.verb)
            in_edges.remove(edge)

    def iterate(self, verbs=None, directions=None, nodes=None):
        verbs = (None,) if not verbs else verbs
        nodes = (None,) if nodes is None else nodes
        directions = Direction.as_tuple(directions, all_if_none=True)

        for verb in ensure_iterable(verbs):
            for direction in ensure_iterable(directions):
                for node in ensure_iterable(nodes):
                    node_key = Node.to_key(node)
                    yield from self._do_iter(verb, node_key, direction)

    def _do_iter(self, verb, node_key, direction):
        edges = self._get_edges(direction, node_key, verb)

        if edges is None:
            pass
        elif isinstance(edges, dict):
            for edge in edges.values():
                for e in edge:
                    yield e.get_other(direction), e
        else:
            for edge in edges:
                yield edge.get_other(direction), edge

    def _get_edges(self, direction, node_key, verb):
        edges = None
        if node_key:
            if direction.is_outgoing:
                edges = self.by_start.get(node_key)
            else:
                edges = self.by_end.get(node_key)
            if edges and verb:
                edges = edges.get(verb)
        elif verb:
            edges = self.by_verb.get(verb)
        return edges
