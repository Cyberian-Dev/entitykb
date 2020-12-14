from pathlib import Path
from typing import Set, Iterator, Optional

from dawg import CompletionDAWG
from diskcache import Index as DiskIndex

from entitykb import Node, Edge, Direction, ensure_iterable


class EdgeIndex(object):
    def __init__(self, root: Path):
        self.dawg_path = root / "edges.dawg"
        self.cache = DiskIndex(str(root / "edges"))
        self.dawg: CompletionDAWG = self._load_dawg()

    def __len__(self) -> int:
        return len(self.cache)

    def __iter__(self) -> Iterator[Edge]:
        for key in self.cache:
            yield self.cache[key]

    def __contains__(self, edge: Edge) -> bool:
        return self.cache.__contains__(edge.key)

    def get_verbs(self) -> Set[str]:
        verbs = set()
        for line in self.dawg.iterkeys(self._vbs):
            verbs.add(line[1:])
        return verbs

    def save(self, edge: Edge):
        self.cache[edge.key] = edge

    def remove(self, edge: Edge) -> Optional[Edge]:
        item = self.cache.pop(edge.key, None)
        return item

    def iterate(self, verbs=None, directions=None, nodes=None):
        verbs = (None,) if not verbs else verbs
        nodes = (None,) if nodes is None else nodes
        directions = Direction.as_tuple(directions, all_if_none=True)

        for verb in ensure_iterable(verbs):
            for direction in ensure_iterable(directions):
                for node in ensure_iterable(nodes):
                    node_key = Node.to_key(node)
                    yield from self._do_iter(verb, node_key, direction)

    def reload(self):
        self.dawg = self._load_dawg()

    def reindex(self):
        self.dawg = self._create_dawg()
        self.dawg.save(self.dawg_path)

    def clear(self):
        self.cache.clear()
        self.reindex()

    def clean(self, node_index):
        for edge in self:
            if edge.start not in node_index:
                self.remove(edge)
            elif edge.end not in node_index:
                self.remove(edge)

    # dawg separators

    _sve = "\1"  # start -> verb -> end -> json
    _vse = "\2"  # verb -> start -> end
    _evs = "\3"  # end -> verb -> start
    _vbs = "\4"  # verb

    # private methods

    def _load_dawg(self):
        if self.dawg_path.is_file():
            return CompletionDAWG().load(str(self.dawg_path))
        return CompletionDAWG([])

    def _create_dawg(self) -> CompletionDAWG:
        def generate_dawg_keys():
            verbs = set()
            for edge in self:
                yield self._sve.join([""] + edge.sve_list)
                yield self._vse.join([""] + edge.vse_list)
                yield self._evs.join([""] + edge.evs_list)
                if edge.verb not in verbs:
                    verbs.add(edge.verb)
                    yield f"{self._vbs}{edge.verb}"

        it_keys = generate_dawg_keys()
        dawg = CompletionDAWG(it_keys)
        return dawg

    def _do_iter(self, verb, node_key, direction):
        sep, tokens = self._get_sep_tokens(direction, node_key, verb)
        if sep:
            prefix = sep.join(tokens)
            for line in self.dawg.iterkeys(prefix):
                edge = self._to_edge(line, sep)
                yield edge.get_other(direction), edge

    def _to_edge(self, line, sep):
        pieces = line.split(sep)
        if sep == self._sve:
            _, s, v, e = pieces

        elif sep == self._vse:
            _, v, s, e = pieces

        else:  # e, v, s
            _, e, v, s = pieces

        return Edge(start=s, verb=v, end=e)

    def _get_sep_tokens(self, direction, node_key, verb):
        sep = None
        tokens = [""]

        if node_key:
            sep = self._sve if direction.is_outgoing else self._evs
            tokens.append(node_key)

        if verb:
            sep = sep or self._vse
            tokens.append(verb)

        return sep, tokens
