from entitykb.models import Entity, FindResult
from entitykb import Config, BaseKB, Graph
from entitykb.pipeline import Pipeline, Normalizer
from entitykb.terms import TermsIndex
from .storage import DefaultStorage


class KB(BaseKB):
    def __init__(self, root: str = None):
        self.uncommitted = 0
        self.config = Config.create(root=root)
        self.storage = DefaultStorage(root=self.config.root)
        self.normalizer = Normalizer.create(self.config.normalizer)
        self.terms = TermsIndex(normalizer=self.normalizer)
        self.graph = Graph()
        self.pipeline = Pipeline.create(
            kb=self, config=self.config, normalizer=self.normalizer
        )
        self.reload()

    def __len__(self):
        return len(self.graph)

    def get_node(self, key: str):
        return self.graph.get_node(key)

    def save_node(self, node):
        self.graph.save_node(node)

        if isinstance(node, Entity):
            self.terms.add_entity(node)

        self.uncommitted += 1
        return self.uncommitted

    def remove_node(self, key):
        raise NotImplementedError

    def save_edge(self, edge):
        return self.graph.save_edge(edge)

    def suggest(self, term, query=None):
        raise NotImplementedError

    def parse(self, text, labels=None):
        doc = self.pipeline(text=text, labels=labels)
        return doc

    def commit(self):
        self.storage.archive()
        py_data = self.terms.get_data(), self.graph.get_data()
        self.storage.save(py_data)

    def reset(self):
        self.terms.reset_data()
        self.graph.reset_data()
        self.commit()
        return True

    def reload(self):
        py_data = self.storage.load()
        if py_data:
            terms_core, graph_core = py_data
            self.terms.put_data(terms_core)
            self.graph.put_data(graph_core)

    def info(self) -> dict:
        return {
            "config": self.config.info(),
            "storage": self.storage.info(),
            "graph": self.graph.info(),
            "terms": self.terms.info(),
        }

    # Local-only KB functions

    def is_prefix(self, prefix) -> bool:
        return self.terms.is_prefix(prefix=prefix)

    def find(self, term: str) -> FindResult:
        term_iter = self.terms.iterate_term_keys(term=term)

        entities = []
        for key in term_iter:
            entity = self.graph.get_node(key)
            entities.append(entity)

        return FindResult(term=term, entities=entities)
