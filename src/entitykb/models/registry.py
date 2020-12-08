from typing import Dict, Type, List

from pydantic import BaseModel, Field

from .entity import Entity
from .node import Node


class Lookup(BaseModel):
    nodes: Dict[str, Type[Node]]

    def __init__(self, **_: Dict):
        nodes = self.load_nodes()
        super().__init__(nodes=nodes)

    # utilities

    def get_subclasses(self, cls):
        # reference: https://stackoverflow.com/a/33607093
        for subclass in cls.__subclasses__():
            yield subclass
            yield from self.get_subclasses(subclass)

    # nodes

    def get_node_class(self, cls: Type[Node], data: dict):
        label = data.get("label")
        found = self.nodes.get(label)

        if cls is Node and found is None and "name" in data:
            found = Entity

        return found or cls

    def load_nodes(self):
        nodes = dict(NODE=Node)
        for node_cls in self.get_subclasses(Node):
            for label in node_cls.get_all_labels():
                nodes[label] = node_cls
        return nodes


class Schema(BaseModel):
    nodes: Dict[str, Dict]
    labels: List[str] = Field(default_factory=list)
    verbs: List[str] = Field(default_factory=list)

    def __init__(self, lookup: Lookup, labels, verbs):
        nodes = self.load_nodes(lookup)
        super().__init__(nodes=nodes, labels=labels, verbs=verbs)

    @classmethod
    def load_nodes(cls, lookup: Lookup):
        nodes = {}
        for (label, node) in lookup.nodes.items():
            nodes[label] = node.schema()
        return nodes


class Registry(object):

    _instance = None

    def __init__(self):
        self.lookup = Lookup()

    def create(self, cls, item=None, **data):
        if isinstance(item, Node):
            return item

        if isinstance(item, dict):
            data = {**item, **data}

        klass = self.identify_class(cls, data)
        return klass(**data)

    def identify_class(self, cls, data: dict):
        klass = None
        if issubclass(cls, Node):
            klass = self.lookup.get_node_class(cls, data=data)

        assert klass, f"Could not identify class: {cls} {data}"

        return klass

    @classmethod
    def instance(cls) -> "Registry":
        if cls._instance is None:
            cls._instance = Registry()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def create_schema(self, labels: List[str], verbs: List[str]):
        return Schema(self.lookup, labels, verbs)
