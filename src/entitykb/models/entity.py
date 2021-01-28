from typing import Any

from .fields import StrTupleField
from .node import Node

ENTITY = "ENTITY"


class Entity(Node):
    name: str = None
    synonyms: StrTupleField = ()

    def __init__(self, **data: Any):
        if not data.get("label"):
            data["label"] = self.get_default_label()
        data.setdefault("key", "{name}|{label}".format(**data))
        if data.get("synonyms", False) is None:
            data["synonyms"] = ()
        super().__init__(**data)

    @property
    def terms(self):
        return (self.name,) + (self.synonyms or ())
