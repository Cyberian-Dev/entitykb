from typing import Optional, Union, Type, List, Iterable

from entitykb.funcs import instantiate_class_from_name
from . import Normalizer, Tokenizer, TokenHandler, KeepLongestByKey
from .model import (
    Doc,
    DocToken,
    DocEntity,
    FindResult,
    Token,
)


class Resolver(object):
    def __init__(
        self, *, tokenizer: Tokenizer, normalizer: Normalizer, kb, **_,
    ):
        self.tokenizer = tokenizer
        self.normalizer = normalizer
        self.kb = kb

    @classmethod
    def is_allowed(cls, _: Iterable[str]):
        return True

    def resolve(
        self,
        *,
        doc,
        doc_tokens: List[DocToken],
        prefix: Token,
        labels: Iterable[str],
    ) -> List[DocEntity]:

        doc_entities = []

        if self.is_allowed(labels):
            doc_entities = self.do_resolve(doc, doc_tokens, prefix, labels)

        return doc_entities

    def do_resolve(
        self, doc, doc_tokens, prefix: str, labels
    ) -> List[DocEntity]:
        doc_entities = []

        find_result = self.find(term=prefix, labels=labels)

        if find_result:
            for entity in find_result:
                doc_entity = DocEntity(
                    text=prefix, doc=doc, entity=entity, tokens=doc_tokens,
                )
                doc_entities.append(doc_entity)

        return doc_entities

    def merge_doc_entities(
        self, doc_entities: List[DocEntity]
    ) -> List[DocEntity]:

        doc_entities = KeepLongestByKey().filter(doc_entities)
        self.clean_doc_tokens(doc_entities)
        return doc_entities

    def clean_doc_tokens(self, doc_entities):
        pass

    def find(self, term: str, labels: Iterable[str] = None) -> FindResult:
        if self.is_allowed(labels):
            return self.do_find(term, labels)

    def do_find(self, term: str, labels: Iterable[str]) -> FindResult:
        raise NotImplementedError

    def is_prefix(self, term: str, labels: Iterable[str] = None) -> bool:
        if self.is_allowed(labels):
            return self.do_is_prefix(term, labels)

    def do_is_prefix(self, term: str, labels) -> bool:
        raise NotImplementedError

    @classmethod
    def create(cls, resolver: "ResolverType" = None, **kwargs) -> "Resolver":

        if isinstance(resolver, str):
            resolver = instantiate_class_from_name(resolver, **kwargs)

        elif not isinstance(resolver, Resolver):
            resolver = (resolver or DefaultResolver)(**kwargs)

        return resolver

    def create_handler(self, doc: Doc, labels):
        return TokenHandler(resolver=self, doc=doc, labels=labels)


class DefaultResolver(Resolver):
    def do_find(self, term: str, labels: Iterable[str]) -> FindResult:
        return self.kb.find(term, labels=labels)

    def do_is_prefix(self, term: str, labels: Iterable[str]) -> bool:
        return self.kb.is_prefix(term, labels=labels)


ResolverType = Optional[Union[Type[Resolver], Resolver, str]]
