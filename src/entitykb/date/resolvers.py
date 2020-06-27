from entitykb import Resolver, FindResult, LabelSet
from . import grammar, Date


class DateResolver(Resolver):

    label_set = LabelSet(labels=["DATE"])

    def do_find(self, term: str, label_set: LabelSet = None) -> FindResult:
        dt = grammar.parse_date(term)

        if dt:
            name = dt.strftime("%Y-%m-%d")
            date = Date(name=name, year=dt.year, month=dt.month, day=dt.day)
            entities = (date,)
            result = FindResult(term=term, entities=entities)
        else:
            result = FindResult(term=term)

        return result

    def do_is_prefix(self, term: str, label_set: LabelSet = None) -> bool:
        is_prefix = grammar.is_prefix(term)
        return is_prefix
