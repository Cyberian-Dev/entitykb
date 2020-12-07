from threading import Lock
from typing import Set

from dawg import CompletionDAWG

from entitykb.models import Node, Edge, Direction, ensure_iterable

lock = Lock()


class BaseEdgeIndex(object):
    def __len__(self):
        raise NotImplementedError

    def get_verbs(self) -> Set[str]:
        raise NotImplementedError

    def save(self, edge: Edge):
        raise NotImplementedError

    def remove(self, edge: Edge):
        raise NotImplementedError

    def iterate(self, verbs=None, directions=None, nodes=None):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError


class EdgeIndex(BaseEdgeIndex):
    # start -> verb -> end -> json
    sve = "\1"

    # verb -> start -> end
    vse = "\2"

    # end -> verb -> start
    evs = "\3"

    def __init__(self):
        self.dawg = CompletionDAWG([])
        self.verb = set()
        self.adds = set()
        self.removes = set()

    def __len__(self):
        count = 0
        for _ in self.dawg.iterkeys(self.sve):
            count += 1
        return count

    def get_verbs(self) -> Set[str]:
        return self.verb

    def save(self, edge: Edge):
        self.adds.add(edge)
        self.removes.discard((edge.start, edge.verb, edge.end))

    def remove(self, edge: Edge):
        self.adds.discard(edge)
        self.removes.add((edge.start, edge.verb, edge.end))

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
        sep, tokens = self._get_sep_tokens(direction, node_key, verb)
        if sep:
            prefix = sep.join(tokens)
            for line in self.dawg.iterkeys(prefix):
                pieces = line.split(sep)
                json = self._get_json(pieces, sep)
                if json is not None:
                    edge = Edge.deserialize(json)
                    yield edge.get_other(direction), edge

    def _get_json(self, pieces, sep):
        if sep == self.sve:
            return pieces[4]

        if sep == self.vse:
            _, v, s, e = pieces

        else:  # e, v, s
            _, e, v, s = pieces

        prefix = self.sve.join(["", s, v, e, ""])
        for item in self.dawg.iterkeys(prefix):
            _, json = item.rsplit(self.sve, maxsplit=1)
            return json

    def _get_sep_tokens(self, direction, node_key, verb):
        sep = None
        tokens = [""]

        if node_key:
            sep = self.sve if direction.is_outgoing else self.evs
            tokens.append(node_key)

        if verb:
            sep = sep or self.vse
            tokens.append(verb)

        return sep, tokens

    def commit(self):
        data = {}
        verbs = set()
        for edge in self.adds:
            if edge not in self.removes:
                verbs.add(edge.verb)
                data[(edge.start, edge.verb, edge.end)] = edge.serialize()

        for item in self.dawg.iterkeys(self.sve):
            _, start, verb, end, json = item.split(self.sve)
            key = (start, verb, end)

            if key not in self.removes and key not in data:
                data[key] = json
                verbs.add(verb)

        combined = []

        for (start, verb, end), json in data.items():
            combined.append(self.sve.join(["", start, verb, end, json]))
            combined.append(self.vse.join(["", verb, start, end]))
            combined.append(self.evs.join(["", end, verb, start]))

        self.dawg = CompletionDAWG(combined)
        self.adds.clear()
        self.removes.clear()
