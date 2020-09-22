from typing import Iterable
from entitykb.pipeline import Resolver, FindResult
from . import grammar, Date


class DateResolver(Resolver):
    def is_allowed(cls, labels: Iterable[str]):
        ok = labels is None
        ok = ok or ("DATE" in labels)
        return ok

    def do_find(self, term: str, labels: Iterable[str]) -> FindResult:
        dt = grammar.parse_date(term)

        if dt:
            name = dt.strftime("%Y-%m-%d")
            date = Date(name=name, year=dt.year, month=dt.month, day=dt.day)
            entities = (date,)
            result = FindResult(term=term, entities=entities)
        else:
            result = FindResult(term=term)

        return result

    def do_is_prefix(self, term: str, labels: Iterable[str]) -> bool:
        is_prefix = grammar.is_prefix(term)
        return is_prefix
