from typing import Optional
from datetime import date
from lark.lark import Lark, Tree
from dateutil import parser
import os


class Parser(object):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            fp = os.path.join(os.path.dirname(__file__), "date.lark")
            grammar = open(fp, "r").read()
            cls._instance = Lark(grammar, parser="lalr")

        return cls._instance


# noinspection PyBroadException
def get_tree(text: str) -> Optional[str]:
    try:
        tree = Parser.instance().parse(text)
        if isinstance(tree.children[0], Tree):
            return tree.children[0].data
    except:
        pass


def is_prefix(text: str) -> bool:
    return get_tree(text) is not None


def is_date(text: str) -> bool:
    return get_tree(text) == "is_date"


# noinspection PyBroadException
def parse_date(text: str) -> Optional[date]:
    if is_date(text):
        try:
            return parser.parse(text).date()
        except:
            pass
