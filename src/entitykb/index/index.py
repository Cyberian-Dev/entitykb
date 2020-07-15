from dataclasses import dataclass
from typing import Optional, Type, Union, Set, List

from entitykb import (
    ER,
    Tokenizer,
    Normalizer,
    Entity,
    EntityValue,
    Relationship,
    FindResult,
)
from entitykb.utils import instantiate_class_from_name
from . import (
    Query,
    QB,
    Storage,
    DefaultStorage,
    Terms,
    DefaultTerms,
    Graph,
    Searcher,
)


@dataclass
class Index(object):
    tokenizer: Tokenizer
    normalizer: Normalizer
    root_dir: str = None
    storage: Storage = None
    terms: Terms = None
    graph: Graph = None
    searcher: Searcher = None

    def __repr__(self):
        return f"<Index: {self.root_dir}>"

    def __call__(self, query):
        return self.find(query=query)

    @property
    def exists(self) -> bool:
        return self.storage.exists

    def info(self) -> dict:
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def add(self, *ent_rels: ER):
        for er in ent_rels:
            if isinstance(er, Entity):
                self.add_entity(er)
            else:
                self.add_relationship(er)

    def add_entity(self, entity: Entity):
        raise NotImplementedError

    def add_relationship(self, relationship: Relationship):
        raise NotImplementedError

    def get_entity(self, val: EntityValue) -> EntityValue:
        raise NotImplementedError

    def is_prefix(self, term: str, labels: Set[str] = None) -> bool:
        raise NotImplementedError

    def find(
        self, term: str = None, labels: Set[str] = None, limit: int = None,
    ) -> FindResult:
        raise NotImplementedError

    def suggest(
        self,
        term: str,
        labels: Set[str] = None,
        query: Query = None,
        limit: int = None,
    ) -> List[str]:
        raise NotImplementedError

    @classmethod
    def create(cls, index: "DefaultIndexType" = None, **kwargs):
        if isinstance(index, str):
            index = instantiate_class_from_name(index, **kwargs)
        elif not isinstance(index, Index):
            index = (index or cls)(**kwargs)
        return index


@dataclass
class DefaultIndex(Index):
    def __post_init__(self):
        if self.storage is None:
            self.storage = DefaultStorage(self.root_dir)

        if self.terms is None:
            self.terms = DefaultTerms(normalizer=self.normalizer)

        if self.graph is None:
            self.graph = Graph()

        if self.searcher is None:
            self.searcher = Searcher(graph=self.graph, terms=self.terms)

    def __repr__(self):
        msg = f"{len(self.graph)} entities, {len(self.terms)} terms"
        return f"<DefaultIndex: {msg}>"

    def __len__(self):
        return len(self.graph)

    def info(self) -> dict:
        return {
            "storage": self.storage.info(),
        }

    def load(self):
        py_data = self.storage.load()
        if py_data:
            terms_core, graph_core = py_data
            self.terms.put_data(terms_core)
            self.graph.put_data(graph_core)

    def commit(self):
        self.storage.archive()
        py_data = self.terms.get_data(), self.graph.get_data()
        self.storage.save(py_data)

    def reset(self):
        self.terms.reset_data()
        self.graph.reset_data()

    def add_entity(self, entity: Entity):
        entity_id = self.graph.add_entity(entity)
        self.terms.add_terms(entity_id, entity.label, entity.terms)
        return entity_id

    def add_relationship(self, relationship: Relationship):
        self.graph.add_relationship(relationship)

    def get_entity(self, val: EntityValue) -> EntityValue:
        return self.graph.get(val)

    def is_prefix(self, term: str, labels: Set[str] = None) -> bool:
        query = QB(prefix=term).filter(label=labels).first()
        entity_it = self.searcher.search(query)

        for _ in entity_it:
            return True
        return False

    def find(
        self, term: str = None, labels: Set[str] = None, limit: int = None,
    ) -> FindResult:

        query = QB(term=term).filter(label=labels).limit(limit)
        results = self.searcher.search(query)

        return FindResult(term=term, entities=results.entities)

    def suggest(
        self,
        prefix: str,
        labels: Set[str] = None,
        query: Query = None,
        limit: int = None,
    ) -> List[str]:

        query = QB(prefix=prefix).filter(label=labels).limit(limit)
        results = self.searcher.search(query)
        return [entity.name for entity in results.entities]


DefaultIndexType = Optional[Union[Type[DefaultIndex], DefaultIndex, str]]
