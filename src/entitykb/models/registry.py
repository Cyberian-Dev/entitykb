from typing import Dict, Type
from pydantic import BaseModel
from .node import Node, Edge
from .entity import Entity


class Lookup(BaseModel):
    nodes: Dict[str, Type[Node]]
    edges: Dict[str, Type[Edge]]

    def __init__(self, **_: Dict):
        nodes = self.load_nodes()
        edges = self.load_edges()
        super().__init__(nodes=nodes, edges=edges)

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

    # edges

    def get_edge_class(self, cls: Type[Edge], data: dict):
        verb = data.get("verb")
        found = self.edges.get(verb)
        return found or cls

    def load_edges(self):
        edges = dict(EDGE=Edge)
        for edge_cls in self.get_subclasses(Edge):
            for verb in edge_cls.get_all_verbs():
                edges[verb] = edge_cls
        return edges


class Schema(BaseModel):
    nodes: Dict[str, Dict]
    edges: Dict[str, Dict]

    def __init__(self, lookup: Lookup):
        nodes = self.load_nodes(lookup)
        edges = self.load_edges(lookup)
        super().__init__(nodes=nodes, edges=edges)

    @classmethod
    def load_nodes(cls, lookup: Lookup):
        nodes = {}
        for (label, node) in lookup.nodes.items():
            nodes[label] = node.schema()
        return nodes

    @classmethod
    def load_edges(cls, lookup: Lookup):
        edges = {}
        for (verb, edge) in lookup.edges.items():
            edges[verb] = edge.schema()
        return edges


class Registry(object):

    _instance = None

    def __init__(self):
        self.lookup = Lookup()
        self.schema = Schema(self.lookup)

    def create(self, cls, item=None, **data):
        if isinstance(item, (Node, Edge)):
            return item

        if isinstance(item, dict):
            data = {**item, **data}

        klass = self.identify_class(cls, data)
        return klass(**data)

    def identify_class(self, cls, data: dict):
        klass = None
        if issubclass(cls, Node):
            klass = self.lookup.get_node_class(cls, data=data)
        elif issubclass(cls, Edge):
            klass = self.lookup.get_edge_class(cls, data=data)

        assert klass, f"Could not identify class: {cls} {data}"

        return klass

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Registry()
        return cls._instance
