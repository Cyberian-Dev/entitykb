from typing import Union, Any
from uuid import uuid4

from pydantic import BaseModel, validator, Field

from .funcs import camel_to_snake


class Node(BaseModel):
    key: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    data: dict = None

    __all_labels__ = {"NODE"}
    __default_label__ = "NODE"

    def __init__(self, **data: Any):
        if not data.get("label"):
            data["label"] = self.get_default_label()
        super().__init__(**data)

    def __hash__(self):
        return hash((self.label, self.key))

    def __rshift__(self, tag):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(Edge, start=self.key, tag=tag, end=None)

    def __lshift__(self, tag):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(Edge, start=None, tag=tag, end=self.key)

    @staticmethod
    def to_key(node_key: Union["Node", str]) -> str:
        return node_key.key if isinstance(node_key, Node) else node_key

    @classmethod
    def get_default_label(cls):
        default_label = cls.__dict__.get("__default_label__")
        if default_label is None:
            default_label = camel_to_snake(cls.__name__, upper=True)
        return default_label

    @classmethod
    def get_all_labels(cls):
        labels = set(cls.__dict__.get("__all_labels__", ()))
        labels.add(cls.get_default_label())
        return labels

    @classmethod
    def create(cls, *args, **kwargs):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(cls, *args, **kwargs)


class Edge(BaseModel):
    start: str = None
    tag: str = None
    end: str = None
    weight: int = 1
    data: dict = None

    __all_tags__ = ()

    @validator("start", "end", pre=True, always=True)
    def node_to_key(cls, v):
        return Node.to_key(v)

    @classmethod
    def get_all_tags(cls):
        tags = set(cls.__dict__.get("__all_tags__", ()))
        return tags

    def __repr__(self):
        return f"<Edge: start={self.start}, tag={self.tag}, end={self.end}>"

    def __rshift__(self, end: Union[Node, str]):
        self.end = Node.to_key(end)
        return self

    def __lshift__(self, start: Union[Node, str]):
        self.start = Node.to_key(start)
        return self

    @classmethod
    def create(cls, *args, **kwargs):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(cls, *args, **kwargs)
