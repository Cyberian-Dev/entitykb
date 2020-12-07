from typing import Union, Any
from uuid import uuid4

from pydantic import BaseModel, validator, Field
from ujson import loads, dumps

from .funcs import camel_to_snake

label_cache = {}


class Serializable(BaseModel):
    def serialize(self) -> str:
        return dumps(self.dict(), escape_forward_slashes=False)

    @classmethod
    def deserialize(cls, json: str):
        data = loads(json)
        return cls.create(**data)

    @classmethod
    def create(cls, *args, **kwargs):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(cls, *args, **kwargs)


class Node(Serializable):
    key: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    data: dict = None

    __all_labels__ = {"NODE"}
    __default_label__ = "NODE"

    def __init__(self, **data: Any):
        if not data.get("label"):
            data["label"] = self.get_default_label()
        super().__init__(**data)

    def __lt__(self, other):
        return self.key < other.key

    def __rshift__(self, verb):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(Edge, start=self.key, verb=verb, end=None)

    def __lshift__(self, verb):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(Edge, start=None, verb=verb, end=self.key)

    @staticmethod
    def to_key(node_key: Union["Node", str]) -> str:
        return node_key.key if isinstance(node_key, Node) else node_key

    @classmethod
    def get_default_label(cls):
        default_label = cls.__dict__.get("__default_label__")
        if default_label is None:
            default_label = label_cache.get(cls.__name__)
            if default_label is None:
                default_label = camel_to_snake(cls.__name__, upper=True)
                label_cache[cls.__name__] = default_label
        return default_label

    @classmethod
    def get_all_labels(cls):
        labels = set(cls.__dict__.get("__all_labels__", ()))
        labels.add(cls.get_default_label())
        return labels


class Edge(Serializable):
    start: str = None
    verb: str = None
    end: str = None
    weight: int = 1
    data: dict = None

    __all_verbs__ = ()

    def __init__(self, *args, **kw):
        from .traverse import Verb

        super().__init__(*args, **kw)
        self.verb = Verb[self.verb]

    def __hash__(self):
        return hash((self.start, self.verb, self.end))

    def __eq__(self, other):
        return (
            other is not None
            and self.start == other.start
            and self.verb == other.verb
            and self.end == other.end
        )

    @validator("start", "end", pre=True, always=True)
    def node_to_key(cls, v):
        return Node.to_key(v)

    @classmethod
    def get_all_verbs(cls):
        verbs = set(cls.__dict__.get("__all_verbs__", ()))
        return verbs

    def __repr__(self):
        return f"<Edge: start={self.start}, verb={self.verb}, end={self.end}>"

    def __rshift__(self, end: Union[Node, str]):
        self.end = Node.to_key(end)
        return self

    def __lshift__(self, start: Union[Node, str]):
        self.start = Node.to_key(start)
        return self

    def get_other(self, direction):
        return self.end if direction.is_outgoing else self.start
