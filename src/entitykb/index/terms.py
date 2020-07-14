from dataclasses import dataclass
from typing import Set, Iterable

from ahocorasick import Automaton as Trie

from entitykb import Normalizer
from . import EID


class TermEntities(object):
    __slots__ = ("term_entity_ids",)

    def __init__(self, entity_id: EID):
        self.term_entity_ids: Set = set()
        if entity_id is not None:
            self.term_entity_ids.add(entity_id)

    def __repr__(self):
        return f"<TermEntities: {self.term_entity_ids}>"

    def iter_exact(self):
        if self.term_entity_ids:
            yield from self.term_entity_ids

    def iter_all(self):
        yield from self.iter_exact()

    def add_term_entity_id(self, entity_id):
        if entity_id not in self.term_entity_ids:
            self.term_entity_ids.add(entity_id)


@dataclass
class Terms(object):
    normalizer: Normalizer
    max_backups: int = 5

    def __repr__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __bool__(self):
        return True

    def get_data(self):
        raise NotImplementedError

    def put_data(self, core):
        raise NotImplementedError

    def reset_data(self):
        raise NotImplementedError

    def info(self) -> dict:
        raise NotImplementedError

    def add_terms(self, entity_id: EID, label: str, terms: Iterable[str]):
        raise NotImplementedError

    def values(self, term: str) -> Iterable[EID]:
        raise NotImplementedError

    def get(self, term: str) -> Iterable[EID]:
        raise NotImplementedError


@dataclass
class DefaultTerms(Terms):

    trie: Trie = None

    def __post_init__(self):
        if self.trie is None:
            self.trie = Trie()

    def __repr__(self):
        return f"<Terms: ({len(self)} terms)>"

    def __len__(self):
        return len(self.trie)

    def get_data(self):
        return self.trie

    def put_data(self, trie: Trie):
        self.trie = trie

    def reset_data(self):
        self.trie = Trie()

    def info(self) -> dict:
        return self.trie.get_stats()

    def add_terms(self, entity_id: EID, label: str, terms: Iterable[str]):
        normalized_terms = []

        for term in terms:
            term = self.normalizer(term)
            normalized_terms.append(term)

            term_entities = self.trie.get(term, None)

            if term_entities is None:
                term_entities = TermEntities(entity_id)
                self.trie.add_word(term, term_entities)
            else:
                term_entities.add_term_entity_id(entity_id)

        return normalized_terms

    def values(self, term: str) -> Iterable[EID]:
        term = self.normalizer(term)
        term_entities = self.trie.values(term)
        seen = set()
        for term_entity in term_entities:
            for entity_id in term_entity.iter_all():
                if entity_id not in seen:
                    yield entity_id
                    seen.add(entity_id)

    def get(self, term: str) -> Iterable[EID]:
        term = self.normalizer(term)
        term_entities = self.trie.get(term, None)
        if term_entities:
            yield from term_entities.iter_exact()
