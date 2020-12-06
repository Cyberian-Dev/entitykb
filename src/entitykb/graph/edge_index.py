from threading import Lock
from typing import Set

from entitykb.models import Node, Edge, Direction, ensure_iterable

lock = Lock()


class EdgeIndex(object):
    def __init__(self):
        self.count = 0

        self.by_start = {}  # start -> {verb -> out_edges}
        self.by_end = {}  # end -> {verb -> in_edges}
        self.by_verb = {}  # verb -> {start -> out_edges}

    def __len__(self):
        return self.count

    def get_verbs(self) -> Set[str]:
        return self.by_verb.keys()

    def save(self, edge):
        with lock:
            start_verb = self.by_start.setdefault(edge.start, {})
            out_edges = start_verb.get(edge.verb)
            any_add, out_edges = self._do_add_edge(edge, out_edges)
            start_verb[edge.verb] = out_edges

            # by_verb is same as by_start, with different key ordering
            self.by_verb.setdefault(edge.verb, {})[edge.start] = out_edges

            # by_end flips the direction of edge
            end_verb = self.by_end.setdefault(edge.end, {})
            in_edges = end_verb.get(edge.verb)
            any_add, in_edges = self._do_add_edge(edge, in_edges)
            end_verb[edge.verb] = in_edges

            if any_add:
                self.count += 1
        return any_add

    @classmethod
    def _do_add_edge(cls, edge, curr_edges):
        any_add = True

        if curr_edges is None:
            curr_edges = edge
        elif isinstance(curr_edges, set):
            if edge in curr_edges:
                any_add = False
            else:
                curr_edges.add(edge)
        elif curr_edges == edge:
            any_add = False
        else:
            curr_edges = {curr_edges, edge}
        return any_add, curr_edges

    def remove(self, edge):
        with lock:
            any_del = self._del_start_edge(edge)
            self._del_end_edge(edge)
            if any_del:
                self.count -= 1
        return any_del

    def _del_start_edge(self, edge):
        any_del = False

        start_verb = self.by_start.get(edge.start)
        if start_verb is not None:
            out_edges = start_verb.get(edge.verb)
            if isinstance(out_edges, Edge):
                if out_edges == edge:
                    del start_verb[edge.verb]
                    del self.by_verb[edge.verb][edge.start]
                    any_del = True

            elif out_edges is not None and edge in out_edges:
                any_del = True
                out_edges.remove(edge)
                if len(out_edges) == 1:
                    out_edges = out_edges.pop()
                    start_verb[edge.verb] = out_edges
                    self.by_verb[edge.verb][edge.start] = out_edges

        return any_del

    def _del_end_edge(self, edge):
        end_verb = self.by_end.get(edge.end)
        if end_verb is not None:
            in_edges = end_verb.get(edge.verb)
            if isinstance(in_edges, Edge):
                if in_edges == edge:
                    del end_verb[edge.verb]

            elif in_edges is not None and edge in in_edges:
                in_edges.remove(edge)
                if len(in_edges) == 1:
                    in_edges = in_edges.pop()
                    end_verb[edge.verb] = in_edges

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
        elif isinstance(edges, Edge):
            yield edges.get_other(direction), edges
        elif isinstance(edges, dict):
            for edge in edges.values():
                if isinstance(edge, set):
                    for e in edge:
                        yield e.get_other(direction), e
                else:
                    yield edge.get_other(direction), edge
        else:
            for edge in edges:
                yield edge.get_other(direction), edge

    def _get_edges(self, direction, node_key, verb):
        edges = None
        if node_key:
            if direction.is_outgoing:
                edges = self.by_start.get(node_key, {})
            else:
                edges = self.by_end.get(node_key, {})
            if verb:
                edges = edges.get(verb)
        elif verb:
            edges = self.by_verb.get(verb)
        return edges
