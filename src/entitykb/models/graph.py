from typing import Union
from uuid import uuid4

from . import ensure_iterable, SlotBase


class Node(SlotBase):

    __slots__ = ["key", "label", "attrs"]

    def __init__(
        self, *, key: str = None, label: str = None, attrs: dict = None, **kw
    ):
        self.key = key or str(uuid4())
        self.label = label
        self.attrs = {**(attrs or {}), **kw}

    def __rshift__(self, tag):
        return Edge(start=self.key, tag=tag, end=None)

    def __lshift__(self, tag):
        return Edge(start=None, tag=tag, end=self.key)

    def __repr__(self):
        return f"<Node: key={self.key} attrs={self.attrs}>"

    def __getattr__(self, item):
        if item == "attrs":
            raise AttributeError

        if item in self.attrs:
            return self.attrs.get(item)
        else:
            raise AttributeError

    @staticmethod
    def to_key(node_key: Union["Node", str]) -> str:
        return node_key.key if isinstance(node_key, Node) else node_key

    @staticmethod
    def to_key_tuple(nodes):
        return tuple(Node.to_key(n) for n in ensure_iterable(nodes))


class Edge(SlotBase):

    __slots__ = ["start", "tag", "end", "weight", "attrs"]

    def __init__(
        self,
        *,
        start: str,
        tag: str,
        end: str,
        weight: int = 1,
        attrs: dict = None,
        **kw,
    ):
        self.start = Node.to_key(start)
        self.tag = tag.upper()
        self.end = Node.to_key(end)
        self.weight = weight
        self.attrs = {**(attrs or {}), **kw}

    def __repr__(self):
        return (
            "<entitykb.graph.model.Edge: "
            f"start={self.start}, tag={self.tag}, end={self.end}>"
        )

    def __rshift__(self, end: Union[Node, str]):
        self.end = Node.to_key(end)
        return self

    def __lshift__(self, start: Union[Node, str]):
        self.start = Node.to_key(start)
        return self
