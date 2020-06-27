from typing import Optional
from datetime import date
from lark.lark import Lark, Tree
from dateutil import parser
import os

fp = os.path.join(os.path.dirname(__file__), "date.lark")
grammar = open(fp, "r").read()
lark_parser = Lark(grammar, parser="lalr")


# noinspection PyBroadException
def get_tree(text: str) -> Optional[str]:
    try:
        tree = lark_parser.parse(text)
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
