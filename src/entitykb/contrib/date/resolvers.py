import datetime
from pathlib import Path
from typing import List

from lark import Token, Tree

from entitykb import Entity, GrammarResolver
from .model import Date


class DateResolver(GrammarResolver):

    allowed_labels = {Date.get_default_label()}
    grammar = Path(__file__).parent / "grammar.lark"

    def create_entities(self, term: str, tree: Tree) -> List[Entity]:
        entities = []
        data = tree_to_data(tree)

        if data:
            try:
                date = Date(synonyms=(term,), **data)
                entities.append(date)
            except ValueError:
                pass

        return entities


def tree_to_data(tree: Tree):
    data, nums = extract_data(tree)

    process_nums(data, nums)

    if data.keys() == {"year", "month", "day"}:
        return data


def extract_data(tree):
    data = {}
    token: Token
    nums = []
    for token in tree.children:
        if token.type == "MONTH_NAME":
            data["month"] = month_names.get(token.value[:3].lower())
        elif token.type == "NUM2":
            nums.append(int(token.value))
        elif token.type != "SEP":
            data[token.type.lower()] = int(token.value)
    return data, nums


def process_nums(data, nums):
    for num in nums:
        if num > 31 and "year" not in data:
            data["year"] = fix_year(num)
        elif num > 12 and "day" not in data:
            data["day"] = num
        elif num > 0 and "month" not in data:
            data["month"] = num
        elif num > 0 and "day" not in data:
            data["day"] = num
        elif "year" not in data:
            data["year"] = fix_year(num)


def fix_year(v):
    if v < 100:
        v += current_century
        if v >= (current_year + 30):
            v -= 100
    return v


current_year = datetime.date.today().year
current_century = (current_year // 100) * 100
month_names = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}
