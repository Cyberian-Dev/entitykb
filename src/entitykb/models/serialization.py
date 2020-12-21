import enum
from typing import Union

from pydantic import BaseModel

from .node import Node, Edge


@enum.unique
class Kind(enum.Enum):
    Node = "Node"
    Edge = "Edge"

    @property
    def is_node(self):
        return self == Kind.Node

    def create(self, payload: dict):
        if self.is_node:
            return Node.create(**payload)
        else:
            return Edge(**payload)


class Envelope(BaseModel):
    kind: Kind = None
    edge: Edge = None
    node: Node = None

    def __init__(self, item: Union[Node, Edge, dict]):
        if isinstance(item, dict):
            # assume Node if no kind found
            item = Kind(item.get("kind", "Node")).create(item.get("payload"))

        if isinstance(item, Node):
            kind = Kind.Node
            node = item
            edge = None

        else:
            kind = Kind.Edge
            node = None
            edge = item

        super().__init__(edge=edge, node=node, kind=kind)

    @property
    def payload(self):
        if self.kind.is_node:
            return self.node
        else:
            return self.edge

    def dict(self):
        return dict(kind=self.kind.value, payload=self.payload)
