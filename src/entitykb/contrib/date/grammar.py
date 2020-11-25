from typing import Optional
from datetime import date
from lark.lark import Lark, Tree
from lark.exceptions import LarkError
from dateutil import parser
from pathlib import Path


class Parser(object):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            fp = Path(__file__).parent / "date.lark"
            grammar = open(fp, "r").read()
            cls._instance = Lark(grammar, parser="lalr")

        return cls._instance


def get_tree(text: str) -> Optional[str]:
    try:
        tree = Parser.instance().parse(text)
        if isinstance(tree.children[0], Tree):
            return tree.children[0].data
    except LarkError:
        pass


def is_prefix(text: str) -> bool:
    return get_tree(text) is not None


def is_date(text: str) -> bool:
    return get_tree(text) == "is_date"


def parse_date(text: str) -> Optional[date]:
    if is_date(text):
        try:
            result = parser.parse(text)
            result = result and result.date()
            return result
        except parser.ParserError:
            pass
