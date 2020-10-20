from typing import Tuple

from . import Node


class Entity(Node):

    __slots__ = ["key", "label", "attrs", "name", "synonyms"]

    def __init__(
        self,
        *,
        name: str,
        label: str = None,
        synonyms: Tuple[str] = None,
        key: str = None,
        attrs: dict = None,
        **kw,
    ):
        self.name = name
        self.synonyms = tuple(synonyms or ())

        label = label or "ENTITY"
        key = key or f"{name}|{label}"

        super().__init__(key=key, label=label, attrs=attrs, **kw)

    def __repr__(self):
        return "<Entity: " f"name={self.name}, label={self.label}>"

    @property
    def terms(self):
        return (self.name,) + (self.synonyms or ())
