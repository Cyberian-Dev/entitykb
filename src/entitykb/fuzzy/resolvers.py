# Performance of Fuzzy Resolver needs to be improved to support long strings
# of text such (i.e. paragraphs, pages, etc.) Some ideas include:
#
#   - Storing these values on the token misspelling:
#       - Correct Token, All Term Tokens, Token Misspell Distance, Entity Key
#       - Collect all of the values for Input Text
#       - Determine if all tokens present for a given term
#       - Calculate Total Distance and Determine if close enough
#       - Potentially run Fuzz Ratio (if needed? maybe distance good enough?)
#


from collections import defaultdict
from typing import List

from rapidfuzz import fuzz

from entitykb import DefaultResolver, DocEntity, Correction, LabelSet


class FuzzyResolver(DefaultResolver):
    def __init__(self, min_ratio=80, **kwargs):
        self.min_ratio = min_ratio
        super().__init__(**kwargs)

    def do_resolve(
        self, doc, doc_tokens, prefix, label_set
    ) -> List[DocEntity]:
        doc_entities = super(FuzzyResolver, self).do_resolve(
            doc=doc, doc_tokens=doc_tokens, prefix=prefix, label_set=label_set
        )

        if not doc_entities:
            doc_entities = self.fuzzy_resolve(
                doc=doc, doc_tokens=doc_tokens, label_set=label_set
            )

        return doc_entities

    def fuzzy_resolve(
        self, *, doc, doc_tokens, label_set: LabelSet
    ) -> List[DocEntity]:
        doc_entities = []
        distances_by_entity = defaultdict(int)
        doc_tokens_by_entity = defaultdict(list)
        conjunctions = []

        for doc_token in doc_tokens:
            token = self.normalizer(doc_token.token)
            if self.index.is_conjunction(token):
                conjunctions.append(doc_token)

            else:
                candidates = self.index.find_candidates(token, label_set)
                for entity, distance in candidates.items():
                    distances_by_entity[entity] += distance
                    doc_tokens_by_entity[entity].append(doc_token)

        for (entity, distance) in distances_by_entity.items():
            entity_doc_tokens = doc_tokens_by_entity[entity]
            entity_doc_tokens += conjunctions
            entity_doc_tokens = sorted(entity_doc_tokens)
            text = self.tokenizer.detokenize(entity_doc_tokens)

            ratio = self.calculate_ratio(entity, text)
            if ratio >= self.min_ratio:
                doc_entity = DocEntity(
                    text=text,
                    doc=doc,
                    entity=entity,
                    tokens=entity_doc_tokens,
                    correction=Correction(distance=distance, ratio=ratio),
                )
                doc_entities.append(doc_entity)

        return doc_entities

    @classmethod
    def calculate_ratio(cls, entity, text) -> int:
        max_ratio = 0.0
        for term in entity.terms:
            ratio = fuzz.token_sort_ratio(term, text)
            max_ratio = max(max_ratio, ratio)

        max_ratio = round(max_ratio)
        return max_ratio

    def clean_doc_tokens(self, doc_entities: List[DocEntity]):
        offset_counts = defaultdict(int)

        for doc_ent in doc_entities:
            for token in doc_ent.tokens:
                if self.index.is_conjunction(token.token):
                    offset_counts[token.offset] += 1

        for offset, count in offset_counts.items():
            if count > 1:
                for doc_ent in doc_entities:
                    doc_ent.tokens = tuple(
                        token
                        for token in doc_ent.tokens
                        if token.offset != offset
                    )
                    doc_ent.text = self.tokenizer.detokenize(doc_ent.tokens)
