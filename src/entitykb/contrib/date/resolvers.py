from typing import List

from entitykb.pipeline import Resolver
from . import grammar, Date


class DateResolver(Resolver):
    allowed_labels = {Date.get_default_label()}

    def resolve(self, term: str) -> List[Date]:
        dt = grammar.parse_date(term)

        entities = []
        if dt:
            name = dt.strftime("%Y-%m-%d")
            date = Date(
                name=name,
                year=dt.year,
                month=dt.month,
                day=dt.day,
                synonyms=(term,),
            )
            entities.append(date)

        return entities

    def is_prefix(self, term: str) -> bool:
        is_prefix = grammar.is_prefix(term)
        return is_prefix
