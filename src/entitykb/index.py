from dataclasses import dataclass
from typing import List, Optional, Any, Type, Union

from . import (
    Store,
    Tokenizer,
    Normalizer,
    Entity,
    Relationship,
    FindResult,
    LabelSet,
    utils,
    DefaultStore,
)

EID = Any


@dataclass
class Index(object):
    tokenizer: Tokenizer
    normalizer: Normalizer
    root_dir: str = None
    store: Store = None

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return f"<Index: {self.root_dir}>"

    def info(self) -> dict:
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def add_entity(self, entity: Entity):
        raise NotImplementedError

    def add_relationship(self, relationship: Relationship):
        raise NotImplementedError

    @classmethod
    def create(cls, index: "DefaultIndexType" = None, **kwargs):
        if isinstance(index, str):
            index = utils.instantiate_class_from_name(index, **kwargs)
        elif not isinstance(index, Index):
            index = (index or cls)(**kwargs)
        return index


@dataclass
class DefaultIndex(Index):
    def __post_init__(self):
        self.store = self.store or DefaultStore(self.root_dir)

    def info(self) -> dict:
        return self.store.info()

    def load(self):
        self.store.load()

    def commit(self):
        self.store.commit()

    def reset(self):
        self.store.reset()

    def add_entity(self, entity: Entity):
        entity_id = self.store.add_entity(entity)

        for term in entity.terms:
            self.add_term(entity, entity_id, term)

    def add_relationship(self, relationship: Relationship):
        self.store.add_relationship(relationship)

    def add_term(self, entity, entity_id, term):
        normalized = self.normalizer(term)
        self.store.add_term(normalized, entity_id)
        return normalized

    def get(self, entity_key: str) -> Entity:
        return self.store.get_entity(entity_key=entity_key)

    def is_prefix(self, prefix: str, label_set: LabelSet = None) -> bool:
        normalized = self.normalizer(prefix)
        return self.store.is_prefix(prefix=normalized, label_set=label_set)

    def find(self, term: str, label_set: LabelSet = None) -> FindResult:
        normalized = self.normalizer(term)
        find_result = self.store.find(term=normalized, label_set=label_set)
        return find_result

    def suggest(
        self, term: str, label_set: LabelSet = None, limit: int = None
    ) -> List[str]:
        normalized = self.normalizer(term)
        return self.store.suggest(
            term=normalized, label_set=label_set, limit=limit
        )


DefaultIndexType = Optional[Union[Type[DefaultIndex], DefaultIndex, str]]
