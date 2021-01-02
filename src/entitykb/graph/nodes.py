from pathlib import Path
from typing import Set, Tuple

from dawg import CompletionDAWG

from entitykb import Node, interfaces, ensure_iterable, istr, create_index


class NodeIndex(object):
    def __init__(self, root: Path, normalizer: interfaces.INormalizer):
        self.normalizer = normalizer
        self.dawg_path = root / "nodes.dawg"
        self.cache = create_index(str(root / "nodes"), decoder=Node.create)
        self.dawg: CompletionDAWG = self._load_dawg()

    def __len__(self) -> int:
        return len(self.cache)

    def __contains__(self, node) -> bool:
        key = Node.to_key(node)
        return self.cache.__contains__(key)

    def get(self, key: str) -> Node:
        try:
            return self.cache[key]
        except KeyError:
            pass

    def save(self, node: Node):
        self.cache[node.key] = node

    def remove(self, node: Node) -> Node:
        key = Node.to_key(node)
        removed = self.cache.pop(key, None)
        return removed

    def get_labels(self) -> Set[str]:
        labels = set()
        for line in self.dawg.iterkeys(self._lbl):
            labels.add(line[1:])
        return labels

    def reload(self):
        self.dawg = self._load_dawg()

    def reindex(self):
        self.dawg = self._create_dawg()
        self.dawg.save(self.dawg_path)

    def clear(self):
        self.cache.clear()
        self.reindex()

    # terms

    def iterate(
        self,
        keys: istr = None,
        terms: istr = None,
        prefixes: istr = None,
        labels: istr = None,
    ):

        allow_prefix = True
        strings = [None]
        if terms:
            strings = ensure_iterable(terms)
            allow_prefix = False
        elif prefixes:
            strings = ensure_iterable(prefixes)

        labels = ensure_iterable(labels) or [None]
        keys = ensure_iterable(keys) or [None]
        for label in labels:
            for key in keys:
                for string in strings:
                    for _, k, is_match in self._do_iter(string, label, key):
                        if allow_prefix or is_match:
                            yield k

    # dawg separators

    _tky = "\1"  # term -> key
    _ltk = "\2"  # label -> term -> key
    _lky = "\3"  # label -> key
    _lbl = "\4"  # label

    # private methods

    def _load_dawg(self):
        if self.dawg_path.is_file():
            return CompletionDAWG().load(str(self.dawg_path))
        return CompletionDAWG([])

    def _create_dawg(self) -> CompletionDAWG:
        def generate_dawg_keys():
            labels = set()
            for node in self.cache.values():
                for term in node.terms:
                    norm = self.normalizer.normalize(term)
                    yield self._tky.join(["", norm, node.key])
                    yield self._ltk.join(["", node.label, norm, node.key])

                yield self._lky.join(["", node.label, node.key])

                if node.label not in labels:
                    labels.add(node.label)
                    yield f"{self._lbl}{node.label}"

        it_keys = generate_dawg_keys()
        dawg = CompletionDAWG(it_keys)
        return dawg

    def _do_iter(self, term=None, label=None, key=None):
        norm = self.normalizer(term) if term else None
        yield from self._do_iter_pair(norm, label, key)

    def _do_iter_pair(self, norm, label, key) -> Tuple[str, str, bool]:
        sep, tokens = self._get_sep_tokens(norm, label, key)

        if sep:
            prefix = sep.join(tokens)
            for line in self.dawg.iterkeys(prefix):
                term, key = self._to_term_key(line, sep)
                yield term, key, term == norm

        else:
            if key:
                keys = [key] if key in self.cache else []
            else:
                keys = self.cache.keys()

            for k in keys:
                yield None, k, False

    def _to_term_key(self, line, sep) -> Tuple[str, str]:
        pieces = line.split(sep)

        if sep == self._tky:
            _, t, k = pieces

        elif sep == self._ltk:
            _, _, t, k = pieces

        else:
            _, l, k = pieces
            t = None

        return t, k

    def _get_sep_tokens(self, norm, label, key):
        sep = False
        tokens = []

        if label and norm:
            sep = self._ltk
            tokens = ["", label, norm] + ([key] if key else [])

        elif norm:
            sep = self._tky
            tokens = ["", norm] + ([key] if key else [])

        elif label:
            sep = self._lky
            tokens = ["", label, key or ""]

        return sep, tokens
