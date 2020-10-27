from typing import Tuple

from . import Node

ENTITY = "ENTITY"


class Entity(Node):

    __all_labels__ = {"ENTITY"}
    __default_label__ = "ENTITY"

    __slots__ = ["key", "label", "data", "name", "synonyms"]

    def __init__(
        self,
        *,
        name: str,
        key: str = None,
        label: str = None,
        data: dict = None,
        synonyms: Tuple[str] = None,
    ):
        self.name = name
        self.synonyms = tuple(synonyms or ())

        label = label or self.get_default_label()
        key = key or f"{name}|{label}"

        super().__init__(key=key, label=label, data=data)

    def __repr__(self):
        return f"<Entity: name={self.name}, label={self.label}>"

    @property
    def terms(self):
        return (self.name,) + (self.synonyms or ())
