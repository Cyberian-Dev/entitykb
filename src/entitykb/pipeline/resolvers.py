import re
from pathlib import Path
from typing import List, Union

from lark import Lark, UnexpectedToken, LarkError, Tree

from entitykb import Entity, interfaces, istr


class TermResolver(interfaces.IResolver):
    def is_prefix(self, term: str, labels: istr = None) -> bool:
        for _ in self.kb.graph.iterate_keys(prefixes=term, labels=labels):
            return True
        return False

    def resolve(self, term: str, labels: istr = None) -> List[Entity]:
        return list(self.kb.graph.iterate_nodes(terms=term, labels=labels))


class RegexResolver(interfaces.IResolver):

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

    def is_prefix(self, term: str, labels: istr = None) -> bool:
        return bool(self.prefix_pattern.fullmatch(term))

    def resolve(self, term: str, labels: istr = None) -> List[Entity]:
        entities = []
        match = self.resolve_pattern.fullmatch(term)
        if match:
            entities = self.create_entities(term, match)
        return entities

    def create_entities(self, term: str, re_match) -> List[Entity]:
        raise NotImplementedError


class GrammarResolver(interfaces.IResolver):
    grammar: Union[str, Path] = None
    parser: str = "lalr"
    start: str = "start"

    def __init__(self, kb=None):
        super().__init__(kb=kb)

        if isinstance(self.grammar, Path):
            data = open(str(self.grammar), "r").read()
        else:
            data = self.grammar  # pragma: no cover

        # noinspection PyTypeChecker
        self.lark = Lark(data, parser=self.parser)

    def resolve(self, term: str, labels: istr = None) -> List[Entity]:
        try:
            tree = self.get_tree(term)
            entities = self.create_entities(term, tree)
        except LarkError:
            entities = []

        return entities

    def get_tree(self, term: str):
        tree = self.lark.parse(term, start=self.start)
        return tree

    def is_prefix(self, term: str, labels: istr = None) -> bool:
        # noinspection PyBroadException
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
