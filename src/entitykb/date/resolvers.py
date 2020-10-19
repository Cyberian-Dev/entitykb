from typing import Iterable
from entitykb.pipeline import Resolver, FindResult
from . import grammar, Date

DATE = "DATE"


class DateResolver(Resolver):
    @classmethod
    def is_relevant(cls, labels: Iterable[str]):
        is_relevant = not bool(labels)
        is_relevant = is_relevant or (DATE in set(labels))
        return is_relevant

    def find(self, term: str) -> FindResult:
        dt = grammar.parse_date(term)

        if dt:
            name = dt.strftime("%Y-%m-%d")
            date = Date(name=name, year=dt.year, month=dt.month, day=dt.day)
            entities = (date,)
            result = FindResult(term=term, entities=entities)
        else:
            result = FindResult(term=term)

        return result

    def is_prefix(self, term: str) -> bool:
        is_prefix = grammar.is_prefix(term)
        return is_prefix
