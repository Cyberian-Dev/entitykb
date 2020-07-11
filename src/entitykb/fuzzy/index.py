from dataclasses import dataclass
from typing import Set

from entitykb import DefaultIndex, LabelSet, utils, Query
from .terms import FuzzyTerms


@dataclass
class FuzzyIndex(DefaultIndex):
    max_token_distance: int = 5
    label_set: LabelSet = LabelSet.create(None)

    def __post_init__(self):
        if self.terms is None:
            self.terms: FuzzyTerms = FuzzyTerms(
                normalizer=self.normalizer,
                tokenizer=self.tokenizer,
                max_token_distance=self.max_token_distance,
                label_set=self.label_set,
            )
        super().__post_init__()

    def is_conjunction(self, token):
        return self.terms.is_conjunction(token)

    def is_prefix(
        self, term: str, labels: Set[str] = None, query: Query = None
    ) -> bool:

        query = Query.convert(query, labels=labels)
        is_prefix = super(FuzzyIndex, self).is_prefix(term, None, query)

        if not is_prefix:
            entity_it = self.terms.edit_values(term=term)
            entity_it = self.engine.search(query, limit=1, entity_it=entity_it)
            for _ in entity_it:
                return True

        return is_prefix

    def find_candidates(self, token: str):
        threshold = self.max_token_distance
        candidates: dict = {}

        edits_iter = utils.generate_edits(token, self.max_token_distance)

        for edit, edit_dist in edits_iter:
            if threshold is None or edit_dist <= threshold:
                for entity_id, entity_dist in self.terms.get_edit(edit):
                    entity_dist += edit_dist
                    threshold = min(threshold, entity_dist)

                    # todo: does this need to create entity?
                    entity = self.get_entity(entity_id)
                    curr = candidates.get(entity, self.max_token_distance)
                    candidates[entity] = min(entity_dist, curr)
            else:
                break

        return candidates
