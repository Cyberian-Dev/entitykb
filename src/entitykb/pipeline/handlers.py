from typing import List, Dict

from entitykb import Doc, DocToken, Span, Token, interfaces, istr


class TokenHandler(object):
    def __init__(self, doc: Doc, resolver: interfaces.IResolver, labels: istr):
        self.doc = doc
        self.resolver = resolver
        self.labels = labels

        self.prefixes: Dict[Token, List[DocToken]] = {}
        self.spans: List[Span] = []

    def __repr__(self):
        return f"<TokenHandler: {self.resolver}>"

    def finalize(self) -> List[Span]:
        for (prefix, doc_tokens) in self.prefixes.items():
            self._resolve_entity(prefix, doc_tokens)
        self.prefixes = {}
        return self.spans

    def handle_token(self, doc_token: DocToken):
        new_prefixes: Dict[Token, List[DocToken]] = {}

        # add this doc_token to existing prefixes and do resolve and is_prefix
        for (prefix, prefix_tokens) in self.prefixes.items():
            candidate = prefix + doc_token.token

            if self.resolver.is_prefix(term=candidate, labels=self.labels):
                new_prefixes[candidate] = prefix_tokens + [doc_token]
            else:
                self._resolve_entity(prefix, prefix_tokens)

        # do resolve and is_prefix for just this doc_token
        if self.resolver.is_prefix(term=doc_token.token, labels=self.labels):
            new_prefixes[doc_token.token] = [doc_token]

        self.prefixes = new_prefixes

    # private methods

    def _resolve_entity(self, prefix: Token, doc_tokens: List[DocToken]):
        any_found = False

        while not any_found and prefix:
            entities = self.resolver.resolve(term=prefix)
            for entity in entities:
                span = Span(
                    text=prefix,
                    doc=self.doc,
                    entity=entity,
                    tokens=doc_tokens,
                )
                self.spans.append(span)
                any_found = True

            if not any_found:
                prefix = prefix.left_token
                doc_tokens = doc_tokens[:-1]
