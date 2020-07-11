import string
from dataclasses import dataclass
from typing import Optional, Set, Iterable, Tuple

from entitykb import LabelSet, Tokenizer
from entitykb.index.terms import EID, DefaultTerms, TermEntities
from entitykb.utils import generate_edits

FUZZ_BLOCK_TOKEN = set(string.punctuation)


class TermEditEntities(TermEntities):
    __slots__ = ("term_entity_ids", "edit_entity_ids", "edit_distance")

    def __init__(self, current: TermEntities = None):
        super().__init__(None)
        self.edit_entity_ids: Optional[Set] = None
        self.edit_distance: int = 9
        if current:
            self.term_entity_ids = current.term_entity_ids

    def __repr__(self):
        attr = [self.term_entity_ids, self.edit_entity_ids, self.edit_distance]
        attr = ", ".join(map(str, attr))
        return f"<TermEditEntities: {attr}>"

    def iter_all(self):
        yield from self.iter_exact()
        if self.edit_entity_ids:
            yield from self.edit_entity_ids

    @classmethod
    def distance(cls, current: TermEntities):
        if isinstance(current, TermEditEntities):
            return current.edit_distance
        else:
            return 0

    @classmethod
    def update(cls, current, entity_id: EID, distance: int) -> TermEntities:
        if isinstance(current, TermEditEntities):
            current.do_add_edit_entity_id(entity_id, distance)

        elif current is None or distance == 0:
            current = TermEditEntities(current)
            current.do_add_edit_entity_id(entity_id, distance)

        return current

    def do_add_edit_entity_id(self, entity_id, distance):
        if not self.edit_entity_ids or entity_id not in self.edit_entity_ids:
            if distance < self.edit_distance:
                self.edit_entity_ids = {entity_id}
                self.edit_distance = distance
            elif distance == self.edit_distance:
                if self.edit_entity_ids:
                    self.edit_entity_ids.add(entity_id)
                else:
                    self.edit_entity_ids = {entity_id}

    def add_term_entity_id(self, entity_id):
        super(TermEditEntities, self).add_term_entity_id(entity_id)
        if self.edit_distance > 0:
            self.edit_distance = 0
            self.edit_entity_ids = None


@dataclass
class FuzzyTerms(DefaultTerms):

    tokenizer: Tokenizer = None
    max_token_distance: int = 5
    label_set: LabelSet = None

    def add_terms(self, entity_id: EID, label: str, terms: Iterable[str]):
        norm_terms = super(FuzzyTerms, self).add_terms(entity_id, label, terms)

        if self.label_set.is_allowed(label):
            for term in norm_terms:
                tokens = self.tokenizer.tokenize(term)
                for token in tokens:
                    if token not in FUZZ_BLOCK_TOKEN:
                        gen = generate_edits(token, self.max_token_distance)
                        for edit, dist in gen:
                            current = self.trie.get(edit, None)
                            updated = TermEditEntities.update(
                                current, entity_id, dist
                            )
                            self.trie.add_word(edit, updated)

        return entity_id

    def edit_values(self, term: str) -> Iterable[EID]:
        last_token = self.get_last_token(term)

        if last_token:
            edit_it = generate_edits(last_token, self.max_token_distance)
            yield from self.generate_edit_ids(edit_it)

    def generate_edit_ids(self, edit_it):
        min_dist_seen = self.max_token_distance
        seen = set()
        for edit, distance in edit_it:
            if distance <= min_dist_seen:
                for eid in super(FuzzyTerms, self).values(edit):
                    if eid not in seen:
                        yield eid
                        seen.add(eid)
                    min_dist_seen = min(min_dist_seen, distance)

    def get_last_token(self, term):
        term = self.normalizer(term)
        tokens = list(self.tokenizer(term))
        while tokens and self.is_conjunction(tokens[-1]):
            tokens = tokens[:-1]
        last_token = tokens and tokens[-1]
        return last_token

    def get_edit(self, edit: str) -> Iterable[Tuple[EID, int]]:
        edit_entities = self.trie.get(edit, None)
        if edit_entities:
            distance = TermEditEntities.distance(edit_entities)
            for entity_id in edit_entities.iter_all():
                yield entity_id, distance

    @property
    def conjunctions(self):
        return DEFAULT_CONJUNCTIONS

    def is_conjunction(self, token):
        return token in self.conjunctions


DEFAULT_CONJUNCTIONS = {
    "or",
    "and",
    ",",
    "(",
    ")",
    ";",
    "+",
    "-",
    "&",
    "[",
    "]",
}
