import re
from pathlib import Path
from typing import Iterable, Set, List, Union

from lark import Lark, UnexpectedToken, LarkError, Tree

from entitykb import create_component, Entity
from .handlers import TokenHandler

ALL_LABELS = object()


class Resolver(object):

    allowed_labels: Set[str] = ALL_LABELS

    def __init__(self, kb=None):
        self.kb = kb

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def get_handler_class(cls):
        return TokenHandler

    @classmethod
    def is_relevant(cls, labels: Iterable[str]):
        if not bool(labels):
            return True

        if cls.allowed_labels == ALL_LABELS:
            return True

        items = set(labels).intersection(cls.allowed_labels)
        return bool(items)

    def resolve(self, term: str) -> List[Entity]:
        raise NotImplementedError

    def is_prefix(self, term: str) -> bool:
        raise NotImplementedError

    @classmethod
    def create(cls, value=None, **kwargs) -> "Resolver":
        return create_component(value, Resolver, TermResolver, **kwargs)


class TermResolver(Resolver):
    def resolve(self, term: str) -> List[Entity]:
        return self.find_entities(self.kb.graph, self.kb.terms, term)

    def is_prefix(self, term: str) -> bool:
        return self.kb.terms.is_prefix(term)

    @classmethod
    def find_entities(cls, graph, terms_index, term: str):
        term_iter = terms_index.iterate_term_keys(term=term)

        entities = []
        for key in term_iter:
            entity = graph.get_node(key)
            entities.append(entity)

        return entities


class RegexResolver(Resolver):

    re_tokens: List[str] = None

    def __init__(self, kb=None):
        super().__init__(kb=kb)

        assert self.re_tokens, f"Class ({self.__class__}) lacks re_tokens."

        prefix_str = ""
        resolve_str = ""
        for re_token in reversed(self.re_tokens):
            if prefix_str:
                prefix_str = f"({prefix_str})?"
            prefix_str = re_token + prefix_str
            resolve_str = f"({re_token})" + resolve_str

        self.prefix_pattern = re.compile(prefix_str)
        self.resolve_pattern = re.compile(resolve_str)

    def is_prefix(self, term: str) -> bool:
        return bool(self.prefix_pattern.fullmatch(term))

    def resolve(self, term: str) -> List[Entity]:
        entities = []
        match = self.resolve_pattern.fullmatch(term)
        if match:
            entities = self.create_entities(term, match)
        return entities

    def create_entities(self, term: str, re_match) -> List[Entity]:
        raise NotImplementedError


class GrammarResolver(Resolver):

    grammar: Union[str, Path] = None
    parser: str = "lalr"
    start: str = "start"

    def __init__(self, kb=None):
        super().__init__(kb=kb)

        if isinstance(self.grammar, Path):
            data = open(self.grammar, "r").read()
        else:
            data = self.grammar  # pragma: no cover

        self.lark = Lark(data, parser=self.parser)

    def resolve(self, term: str) -> List[Entity]:
        try:
            tree = self.lark.parse(term, start=self.start)
            entities = self.create_entities(term, tree)
        except LarkError:
            entities = []

        return entities

    def is_prefix(self, term: str) -> bool:
        try:
            self.lark.parse(term, start=self.start)
            is_prefix = True
        except UnexpectedToken as e:
            is_prefix = e.token.type == "$END"
        except Exception:
            is_prefix = False

        return is_prefix

    def create_entities(self, term: str, tree: Tree) -> List[Entity]:
        raise NotImplementedError
