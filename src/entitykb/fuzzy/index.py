from dataclasses import dataclass
from typing import Set

from entitykb import DefaultIndex, LabelSet, utils, QB
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

    def is_prefix(self, term: str, labels: Set[str] = None) -> bool:
        is_prefix = super(FuzzyIndex, self).is_prefix(term, labels)

        if not is_prefix:
            entity_it = self.terms.edit_values(term=term)
            query = QB(entity_it).filter(label=labels).first()
            entity_it = self.searcher.search(query)

            for _ in entity_it:
                return True

        return is_prefix

    def find_candidates(self, token: str, label_set: LabelSet = None):
        threshold = self.max_token_distance
        candidates: dict = {}

        edits_iter = utils.generate_edits(token, self.max_token_distance)
        label_set = self.label_set.intersect(label_set)

        for edit, edit_dist in edits_iter:
            if threshold is None or edit_dist <= threshold:
                for entity_id, entity_dist in self.terms.get_edit(edit):
                    entity_dist += edit_dist
                    threshold = min(threshold, entity_dist)

                    # todo: does this need to create entity?
                    entity = self.get_entity(entity_id)
                    if label_set.is_allowed(entity.label):
                        curr = candidates.get(entity, self.max_token_distance)
                        candidates[entity] = min(entity_dist, curr)
            else:
                break

        return candidates
