from typing import Optional, Union, Type, Iterable

from entitykb.funcs import instantiate_class_from_name
from . import Normalizer, Tokenizer, TokenHandler, FindResult


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
        return self.kb.find(term)

    def is_prefix(self, term: str) -> bool:
        return self.kb.is_prefix(term)


ResolverType = Optional[Union[Type[Resolver], Resolver, str]]
