from typing import Optional, Union, Type, Iterable

from . import Normalizer, Tokenizer, TokenHandler
from entitykb.models import instantiate_class_from_name, FindResult


class Resolver(object):
    def __init__(
        self, *, tokenizer: Tokenizer, normalizer: Normalizer, kb, **_,
    ):
        self.tokenizer = tokenizer
        self.normalizer = normalizer
        self.kb = kb

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def get_handler_class(cls):
        return TokenHandler

    @classmethod
    def is_relevant(cls, labels: Iterable[str]):
        return True

    def find(self, term: str) -> FindResult:
        raise NotImplementedError

    def is_prefix(self, term: str) -> bool:
        raise NotImplementedError

    @classmethod
    def create(cls, resolver: "ResolverType" = None, **kwargs) -> "Resolver":
        if isinstance(resolver, str):
            resolver = instantiate_class_from_name(resolver, **kwargs)

        elif not isinstance(resolver, Resolver):
            resolver = (resolver or DefaultResolver)(**kwargs)

        return resolver


class DefaultResolver(Resolver):
    def find(self, term: str) -> FindResult:
        term_iter = self.kb.terms.iterate_term_keys(term=term)

        entities = []
        for key in term_iter:
            entity = self.kb.graph.get_node(key)
            entities.append(entity)

        return FindResult(term=term, entities=entities)

    def is_prefix(self, term: str) -> bool:
        return self.kb.terms.is_prefix(term)


ResolverType = Optional[Union[Type[Resolver], Resolver, str]]
