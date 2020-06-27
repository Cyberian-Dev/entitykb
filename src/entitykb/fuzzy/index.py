import string

from entitykb import (
    DefaultIndex,
    LabelSet,
    utils,
)
from .store import FuzzyStore

FUZZ_BLOCK_TOKEN = set(string.punctuation)
MAX_TOKEN_DISTANCE = 5


class FuzzyIndex(DefaultIndex):

    label_set = LabelSet.create(None)

    def __init__(
        self,
        *,
        root_dir: str = None,
        conjunctions=None,
        max_token_distance=2,
        **kwargs,
    ):
        store = FuzzyStore(root_dir)
        super().__init__(root_dir=root_dir, store=store, **kwargs)

        self.conjunctions = conjunctions or DEFAULT_CONJUNCTIONS
        self.max_token_distance = max_token_distance

    def add_term(self, entity, entity_id, term):
        normalized = super(FuzzyIndex, self).add_term(entity, entity_id, term)

        if self.label_set.is_allowed(entity.label):
            for token in self.tokenizer.tokenize(normalized):
                if token not in FUZZ_BLOCK_TOKEN:
                    gen = utils.generate_edits(token, self.max_token_distance)
                    for edit, dist in gen:
                        self.store.upsert_edit(edit, dist, entity_id)

    def is_prefix(self, prefix: str, label_set: LabelSet = None) -> bool:
        is_prefix = super(FuzzyIndex, self).is_prefix(prefix, label_set)
        is_prefix = is_prefix or self.is_edit_prefix(prefix, label_set)
        return is_prefix

    def is_edit_prefix(self, prefix: str, label_set: LabelSet):
        is_prefix = False
        fuzzy_label_set = self.label_set.intersect(label_set)

        if fuzzy_label_set:
            normalized = self.normalizer(prefix)
            last_token = list(self.tokenizer(normalized))[-1]

            if self.is_conjunction(last_token):
                return True

            ed_iter = utils.generate_edits(last_token, self.max_token_distance)
            for edit, distance in ed_iter:
                if self.store.is_prefix(edit, fuzzy_label_set):
                    is_prefix = True
                    break

        return is_prefix

    def is_conjunction(self, token):
        return token in self.conjunctions

    def find_candidates(self, token: str, label_set: LabelSet):
        threshold = self.max_token_distance
        candidates: dict = {}

        edits_iter = utils.generate_edits(token, self.max_token_distance)
        fuzzy_label_set = self.label_set.intersect(label_set)

        for edit, edit_dist in edits_iter:
            if threshold is None or edit_dist <= threshold:
                find_result = self.store.find_edit(edit, fuzzy_label_set)
                for entity in find_result.entities:
                    entity_dist = find_result.distance + edit_dist
                    threshold = min(threshold, entity_dist)
                    current = candidates.get(entity, MAX_TOKEN_DISTANCE)
                    candidates[entity] = min(entity_dist, current)
            else:
                break

        return candidates


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
