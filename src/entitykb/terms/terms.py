from typing import Iterable

from entitykb import Entity, Normalizer, create_component
from dawg import CompletionDAWG


class TermsIndex(object):
    def __init__(self, normalizer: Normalizer):
        self.normalizer = normalizer

    def get_data(self):
        raise NotImplementedError

    def put_data(self, data):
        raise NotImplementedError

    def clear_data(self):
        raise NotImplementedError

    def info(self) -> dict:
        raise NotImplementedError

    def commit(self):
        pass

    def add_entity(self, entity: Entity, **kwargs):
        key = Entity.to_key(entity)
        for term in entity.terms:
            self.add_term(key=key, term=term, **kwargs)

    def remove_entity(self, entity: Entity):
        key = Entity.to_key(entity)
        for term in entity.terms:
            self.remove_term(key=key, term=term)

    def add_term(self, key: str, term: str):
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
        if value is None and cls != TermsIndex:
            value = cls
        return create_component(value, TermsIndex, DawgTermsIndex, **kwargs)


class DawgTermsIndex(TermsIndex):
    sep = "\1"

    def __init__(self, normalizer: Normalizer):
        super().__init__(normalizer)
        self.dawg = CompletionDAWG([])
        self.adds = {}
        self.removes = {}

    def __len__(self):
        return len(self.dawg.keys())

    def get_data(self):
        return self.dawg.keys()

    def put_data(self, data):
        self.dawg = CompletionDAWG(data)

    def clear_data(self):
        self.dawg = CompletionDAWG([])

    def info(self) -> dict:
        return dict(count=len(self))

    def commit(self):
        for encoded_key in self.dawg.iterkeys():
            pieces = encoded_key.split(self.sep)
            term, keys = pieces[0], set(pieces[1:])

            if term in self.adds or term in self.removes:
                keys -= self.removes.get(term, set())
                keys |= self.adds.get(term, set())
                self.adds[term] = keys

        combined = []
        for term, keys in self.adds.items():
            encoded_key = self.sep.join([term] + sorted(keys))
            combined.append(encoded_key)

        self.dawg = CompletionDAWG(combined)
        self.adds.clear()
        self.removes.clear()

    def add_term(self, key: str, term: str):
        normalized = self.normalizer(term)
        self.adds.setdefault(normalized, set()).add(key)
        try:
            self.removes.setdefault(normalized, set()).remove(key)
        except KeyError:
            pass

        return normalized

    def remove_term(self, key: str, term: str):
        normalized = self.normalizer(term)
        try:
            self.adds.setdefault(normalized, set()).remove(key)
        except KeyError:
            pass
        self.removes.setdefault(normalized, set()).add(key)

    def is_prefix(self, prefix: str) -> bool:
        normalized = self.normalizer(prefix)
        return self.dawg.has_keys_with_prefix(normalized)

    def iterate_prefix_keys(self, prefix: str) -> Iterable[str]:
        yield from self.iterate(prefix, prefix_check=True)

    def iterate_term_keys(self, term: str) -> Iterable[str]:
        yield from self.iterate(term, prefix_check=False)

    def iterate(self, search: str, prefix_check: bool) -> Iterable[str]:
        normalized = self.normalizer(search)
        for entry in self.dawg.iterkeys(normalized):
            pieces = entry.split(self.sep)
            if prefix_check or normalized == pieces[0]:
                for key in pieces[1:]:
                    yield key
