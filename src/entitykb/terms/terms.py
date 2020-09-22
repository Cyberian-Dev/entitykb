from typing import Callable, Iterable
from ahocorasick import Automaton as Trie
from entitykb.graph import Node


class Terms(object):

    __slots__ = ("trie", "normalizer")

    def __init__(self, normalizer: Callable, trie: Trie = None):
        self.normalizer = normalizer
        self.trie = trie or Trie()

    def add_term(self, term: str, node: Node, **meta):
        normalized = self.normalizer(term)
        key = Node.to_key(node)
        entry = self.trie.get(normalized, None)

        if entry is None:
            entry = set()
            self.trie.add_word(normalized, entry)

        if not meta:
            meta = None

        entry.add((key, meta))
        return normalized

    def is_prefix(self, term: str):
        normalized = self.normalizer(term)
        return self.trie.match(normalized)

    def iterate_prefix_keys(self, prefix: str) -> Iterable[str]:
        for entry in self.trie.values(prefix):
            for key, meta in entry:
                yield key

    def iterate_term_keys(self, term: str) -> Iterable[str]:
        term = self.normalizer(term)
        entry = self.trie.get(term, ())
        for key, meta in entry:
            yield key
