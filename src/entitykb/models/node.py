from typing import Union
from uuid import uuid4

from . import SlotBase, camel_to_snake, Tag


class NodeLabelRegistry(object):

    _instance = None

    def __init__(self):
        self.values = dict(NODE=Node)

        for cls in Node.__all_subclasses__():
            for label in cls.get_all_labels():
                self.values[label] = cls

    def get_node_cls(self, label):
        return self.values.get(label)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = NodeLabelRegistry()
        return cls._instance


class Node(SlotBase):

    __slots__ = ["key", "label", "data"]
    __all_labels__ = {"NODE"}
    __default_label__ = "NODE"

    def __init__(
        self, *, key: str = None, label: str = None, data: dict = None
    ):
        self.key = key or str(uuid4())
        self.label = label or self.__default_label__
        self.data = data

    def __hash__(self):
        return hash((self.label, self.key))

    def __rshift__(self, tag):
        return Edge(start=self.key, tag=tag, end=None)

    def __lshift__(self, tag):
        return Edge(start=None, tag=tag, end=self.key)

    @classmethod
    def __all_subclasses__(cls):
        # reference: https://stackoverflow.com/a/33607093
        for subclass in cls.__subclasses__():  # type: Node
            yield subclass
            yield from subclass.__all_subclasses__()

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
        yield cls.get_default_label()
        yield from cls.__dict__.get("__all_labels__", ())

    @classmethod
    def identify_klass(cls, kwargs):
        label = kwargs.get("label")
        klass = NodeLabelRegistry.instance().get_node_cls(label)
        if klass is None and cls == Node and "name" in kwargs:
            from .entity import Entity

            return Entity
        return klass


class Edge(SlotBase):

    __slots__ = ["start", "tag", "end", "weight", "data"]

    def __init__(
        self,
        *,
        start: str,
        tag: Tag,
        end: str,
        weight: int = 1,
        data: dict = None,
    ):
        self.start = Node.to_key(start)
        self.tag = Tag(tag)
        self.end = Node.to_key(end)
        self.weight = weight
        self.data = data

    def __repr__(self):
        return f"<Edge: start={self.start}, tag={self.tag}, end={self.end}>"

    def __rshift__(self, end: Union[Node, str]):
        self.end = Node.to_key(end)
        return self

    def __lshift__(self, start: Union[Node, str]):
        self.start = Node.to_key(start)
        return self
