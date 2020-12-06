from typing import Iterable

from ahocorasick import Automaton as Trie
from entitykb import Entity, Normalizer, create_component, SmartList


class TermsIndex(object):
    def __init__(self, normalizer: Normalizer):
        self.normalizer = normalizer

    def get_data(self):
        raise NotImplementedError

    def put_data(self, trie: Trie):
        raise NotImplementedError

    def clear_data(self):
        raise NotImplementedError

    def info(self) -> dict:
        raise NotImplementedError

    def add_entity(self, entity: Entity, **kwargs):
        raise NotImplementedError

    def add_term(self, key: str, term: str):
        raise NotImplementedError

    def remove_entity(self, entity: Entity):
        raise NotImplementedError

    def remove_term(self, key: str, term: str):
        raise NotImplementedError

    def is_prefix(self, prefix: str) -> bool:
        raise NotImplementedError

    def iterate_prefix_keys(self, prefix: str) -> Iterable[str]:
        raise NotImplementedError

    def iterate_term_keys(self, term: str) -> Iterable[str]:
        raise NotImplementedError

    @classmethod
    def create(cls, value=None, **kwargs) -> "TermsIndex":
        return create_component(value, TermsIndex, TrieTermsIndex, **kwargs)


class TrieTermsIndex(TermsIndex):
    def __init__(self, normalizer: Normalizer):
        super().__init__(normalizer)
        self.trie = Trie()

    def __len__(self):
        return len(self.trie)

    def get_data(self):
        return self.trie

    def put_data(self, trie: Trie):
        self.trie = trie

    def clear_data(self):
        self.trie = Trie()

    def info(self) -> dict:
        return self.trie.get_stats()

    def add_entity(self, entity: Entity, **kwargs):
        key = Entity.to_key(entity)
        for term in entity.terms:
            self.add_term(key=key, term=term, **kwargs)

    def add_term(self, key: str, term: str):
        normalized = self.normalizer(term)
        entry = self.trie.get(normalized, None)

        if entry is None:
            entry = SmartList()
            self.trie.add_word(normalized, entry)

        if key:
            entry.append(key)

        return normalized

    def remove_entity(self, entity: Entity):
        key = Entity.to_key(entity)
        for term in entity.terms:
            self.remove_term(key=key, term=term)

    def remove_term(self, key: str, term: str):
        normalized = self.normalizer(term)
        entry = self.trie.get(normalized, None)
        entry.remove(key)

        if not entry:
            self.trie.remove_word(normalized)
        else:
            self.trie.add_word(normalized, entry)

    def is_prefix(self, prefix: str) -> bool:
        normalized = self.normalizer(prefix)
        return self.trie.match(normalized)

    def iterate_prefix_keys(self, prefix: str) -> Iterable[str]:
        normalized = self.normalizer(prefix)
        for entry in self.trie.values(normalized):
            for key in entry:
                yield key

    def iterate_term_keys(self, term: str) -> Iterable[str]:
        normalized = self.normalizer(term)
        entry = self.trie.get(normalized, ())
        for key in entry:
            yield key
