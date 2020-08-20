from typing import List, Dict

from . import Doc, DocToken, DocEntity, Token, LabelSet


class TokenHandler(object):
    def __init__(self, resolver, label_set: LabelSet, doc: Doc):
        self.resolver = resolver
        self.label_set = label_set
        self.doc = doc

        self.prefixes: Dict[Token, List[DocToken]] = {}
        self.doc_entities: List[DocEntity] = []

    def get_doc_entities(self) -> List[DocEntity]:
        # process any incomplete prefixes
        for (prefix, doc_tokens) in self.prefixes.items():
            self.resolve_entity(prefix, doc_tokens)
        self.prefixes = {}
        self.doc_entities = self.resolver.merge_doc_entities(self.doc_entities)
        return self.doc_entities

    def handle_token(self, doc_token: DocToken):
        new_prefixes: Dict[Token, List[DocToken]] = {}

        # add this doc_token to existing prefixes and do resolve and is_prefix
        for (prefix, prefix_tokens) in self.prefixes.items():
            candidate = prefix + doc_token.token

            if self.resolver.is_prefix(
                term=candidate, label_set=self.label_set
            ):
                new_prefixes[candidate] = prefix_tokens + [doc_token]

            self.resolve_entity(prefix, prefix_tokens)

        # do resolve and is_prefix for just this doc_token
        if self.resolver.is_prefix(
            term=doc_token.token, label_set=self.label_set
        ):
            new_prefixes[doc_token.token] = [doc_token]

        self.prefixes = new_prefixes

    def resolve_entity(self, prefix: Token, doc_tokens: List[DocToken]):
        doc_entities = []

        while not doc_entities and prefix:
            doc_entities = self.resolver.resolve(
                doc=self.doc,
                prefix=prefix,
                label_set=self.label_set,
                doc_tokens=doc_tokens,
            )

            if not doc_entities:
                prefix = prefix.left_token
                doc_tokens = doc_tokens[:-1]

        self.doc_entities += doc_entities
