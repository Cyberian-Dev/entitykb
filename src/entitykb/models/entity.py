from typing import Tuple, Any

from .node import Node

ENTITY = "ENTITY"


class Entity(Node):
    name: str = None
    synonyms: Tuple[str, ...] = ()

    def __init__(self, **data: Any):
        if not data.get("label"):
            data["label"] = self.get_default_label()
        data.setdefault("key", "{name}|{label}".format(**data))
        super().__init__(**data)

    @property
    def terms(self):
        return (self.name,) + (self.synonyms or ())
