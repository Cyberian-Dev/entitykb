from typing import List, Dict

from .model import Doc, DocToken, DocEntity, Token


class TokenHandler(object):
    def __init__(self, doc: Doc, resolver):
        self.doc = doc
        self.resolver = resolver

        self.prefixes: Dict[Token, List[DocToken]] = {}
        self.doc_entities: List[DocEntity] = []

    def __repr__(self):
        return f"<TokenHandler: {self.resolver}>"

    def finalize(self) -> List[DocEntity]:
        for (prefix, doc_tokens) in self.prefixes.items():
            self._resolve_entity(prefix, doc_tokens)
        self.prefixes = {}
        return self.doc_entities

    def handle_token(self, doc_token: DocToken):
        new_prefixes: Dict[Token, List[DocToken]] = {}

        # add this doc_token to existing prefixes and do resolve and is_prefix
        for (prefix, prefix_tokens) in self.prefixes.items():
            candidate = prefix + doc_token.token

            if self.resolver.is_prefix(term=candidate):
                new_prefixes[candidate] = prefix_tokens + [doc_token]
            else:
                self._resolve_entity(prefix, prefix_tokens)

        # do resolve and is_prefix for just this doc_token
        if self.resolver.is_prefix(term=doc_token.token):
            new_prefixes[doc_token.token] = [doc_token]

        self.prefixes = new_prefixes

    # private methods

    def _resolve_entity(self, prefix: Token, doc_tokens: List[DocToken]):
        any_found = False

        while not any_found and prefix:
            find_result = self.resolver.find(term=prefix)
            for entity in find_result:
                doc_entity = DocEntity(
                    text=prefix,
                    doc=self.doc,
                    entity=entity,
                    tokens=doc_tokens,
                )
                self.doc_entities.append(doc_entity)
                any_found = True

            if not any_found:
                prefix = prefix.left_token
                doc_tokens = doc_tokens[:-1]
