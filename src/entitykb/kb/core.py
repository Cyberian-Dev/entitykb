from typing import Optional, Union

from entitykb import (
    Config,
    BaseKB,
    InMemoryGraph,
    Node,
    Entity,
    Edge,
    Registry,
    Searcher,
    Pipeline,
    Normalizer,
    TermsIndex,
)
from .storage import PickleStorage
from importlib import import_module


class KB(BaseKB):
    def __init__(self, root: str = None):
        self.uncommitted = 0
        self.config = Config.create(root=root)
        self.storage = PickleStorage(root=self.config.root)
        self.normalizer = Normalizer.create(self.config.normalizer)
        self.terms = TermsIndex(normalizer=self.normalizer)
        self.graph = InMemoryGraph()
        self.searcher = Searcher(graph=self.graph)
        self.pipeline = Pipeline.create(
            kb=self, config=self.config, normalizer=self.normalizer
        )
        self.modules = [import_module(m) for m in self.config.modules]

        self.reload()

    # common

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.graph)

    def save(self, item):
        if isinstance(item, Node):
            return self.save_node(item)
        elif isinstance(item, Edge):
            return self.save_edge(item)
        else:
            raise RuntimeError(f"Unknown item type: {type(item)}")

    # nodes

    def get_node(self, key: str) -> Optional[Node]:
        return self.graph.get_node(key)

    def save_node(self, node: Union[Node, dict]) -> Node:
        node = Registry.instance().create(Node, node)

        self.graph.save_node(node)

        if isinstance(node, Entity):
            self.terms.add_entity(node)

        return node

    def remove_node(self, key) -> bool:
        return self.graph.remove_node(key)

    # edges

    def save_edge(self, edge):
        return self.graph.save_edge(edge)

    def suggest(self, term, query=None):
        raise NotImplementedError

    def parse(self, text, *labels):
        doc = self.pipeline(text=text, labels=labels)
        return doc

    # admin

    def commit(self):
        self.storage.archive()
        py_data = self.terms.get_data(), self.graph.get_data()
        self.storage.save(py_data)
        return True

    def clear(self):
        self.terms.clear_data()
        self.graph.clear_data()
        return True

    def reload(self):
        py_data = self.storage.load()
        if py_data:
            terms_core, graph_core = py_data
            self.terms.put_data(terms_core)
            self.graph.put_data(graph_core)
        return True

    def info(self) -> dict:
        return {
            "config": self.config.info(),
            "storage": self.storage.info(),
            "graph": self.graph.info(),
            "terms": self.terms.info(),
        }

    @classmethod
    def get_schema(cls) -> dict:
        return Registry.instance().schema.dict()
