from .base import SlotBase


class FindResult(SlotBase):

    __slots__ = ("term", "entities")

    def __init__(self, term: str, entities=None):
        self.term = term
        self.entities = entities or ()

    def __repr__(self):
        keys = ", ".join(map(lambda e: e.key, self.entities))
        return f"{self.term} [{keys}]"

    def __len__(self):
        return len(self.entities)

    def __iter__(self):
        return iter(self.entities)
