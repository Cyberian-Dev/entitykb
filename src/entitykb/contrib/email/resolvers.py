import re
from typing import List, Iterable

from entitykb import Resolver
from .model import Email


class EmailResolver(Resolver):
    @classmethod
    def is_relevant(cls, labels: Iterable[str]):
        is_relevant = not bool(labels)
        is_relevant = is_relevant or (Email.get_default_label() in labels)
        return is_relevant

    prefix_pattern = re.compile(
        r"[a-zA-Z0-9_.+-]+(@([a-zA-Z0-9-]+(\.([a-zA-Z0-9-.]+)?)?)?)?"
    )

    def is_prefix(self, term: str) -> bool:
        return self.prefix_pattern.fullmatch(term)

    resolve_pattern = re.compile(
        r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    )

    def resolve(self, term: str) -> List[Email]:
        entities = []
        match = self.resolve_pattern.fullmatch(term)
        if match:
            entity = Email(name=term, username=match[1], domain=match[2])
            entities.append(entity)
        return entities
