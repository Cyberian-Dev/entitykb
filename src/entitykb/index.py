import os
from typing import List, Optional, Any, Type, Union

from . import (
    Store,
    Tokenizer,
    Normalizer,
    Entity,
    FindResult,
    LabelSet,
    utils,
    DefaultStore,
)

EID = Any


class Index(object):
    @classmethod
    def create(cls, index: "DefaultIndexType" = None, **kwargs):
        if isinstance(index, str):
            index = utils.instantiate_class_from_name(index, **kwargs)
        elif not isinstance(index, Index):
            index = (index or cls)(**kwargs)
        return index


class DefaultIndex(Index):
    def __init__(
        self,
        *,
        root_dir: str = None,
        tokenizer: Tokenizer,
        normalizer: Normalizer,
        max_backups=5,
        store: Store = None,
    ):
        self.root_dir = root_dir
        self.tokenizer = tokenizer
        self.normalizer = normalizer
        self.max_backups = max(0, max_backups)
        self.store = DefaultStore(self.root_dir) if store is None else store

    def __len__(self):
        return len(self.store)

    @property
    def exists(self):
        return bool(self.store is not None and self.store.exists)

    @property
    def index_path(self):
        return self.store is not None and self.store.index_path

    def add(self, entity: Entity):
        entity_id = self.store.upsert_entity(entity)

        for term in entity.terms:
            self.add_term(entity, entity_id, term)

    def add_term(self, entity, entity_id, term):
        normalized = self.normalizer(term)
        self.store.upsert_term(normalized, entity_id, entity.label)
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

    def info(self) -> dict:
        return self.store.info()

    def load(self):
        self.store.load()

    def commit(self):
        self.backup_index()
        self.store.commit()

    def reset(self):
        self.store.reset()

    # backups

    @property
    def backup_dir(self):
        backup_dir = os.path.join(self.root_dir, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def backup_index(self) -> Optional[str]:
        if self.exists and self.max_backups:
            backup_path = self.store.archive(self.backup_dir)
            self.clean_backups()
            return backup_path

    def get_backups(self):
        paths = [f"{self.backup_dir}/{x}" for x in os.listdir(self.backup_dir)]
        paths = sorted(paths, key=os.path.getctime)
        return paths

    def clean_backups(self) -> Optional[str]:
        backups = self.get_backups()

        if len(backups) >= self.max_backups:
            oldest = backups[0]
            os.remove(oldest)
            return oldest


DefaultIndexType = Optional[Union[Type[DefaultIndex], DefaultIndex, str]]
