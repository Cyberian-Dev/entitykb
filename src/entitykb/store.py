import os
import pickle
import time
from typing import Dict, List, Optional, Any, Set

import ahocorasick

from . import Entity, FindResult, LabelSet, utils, logger

EID = Any


class TermEntities(object):
    __slots__ = ("term_entity_ids",)

    def __init__(self, entity_id: EID):
        self.term_entity_ids: Set = set()
        if entity_id is not None:
            self.term_entity_ids.add(entity_id)

    def __str__(self):
        return f"<TermEntities: {self.term_entity_ids}>"

    def __iter__(self):
        if self.term_entity_ids:
            yield from self.term_entity_ids

    def add_term_entity_id(self, entity_id):
        if entity_id not in self.term_entity_ids:
            self.term_entity_ids.add(entity_id)


class Store(object):
    def __len__(self):
        raise NotImplementedError

    @property
    def exists(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def upsert_entity(self, entity: Entity) -> EID:
        raise NotImplementedError

    def upsert_term(self, term: str, entity_id: EID, label: str):
        raise NotImplementedError

    def get_entity(self, entity_key: str) -> Entity:
        raise NotImplementedError

    def is_prefix(self, prefix: str, label_set: LabelSet = None) -> bool:
        raise NotImplementedError

    def get_term_entities(self, term: str) -> TermEntities:
        raise NotImplementedError

    def find(self, term: str, label_set: LabelSet = None) -> FindResult:
        raise NotImplementedError

    def suggest(
        self, term: str, label_set: LabelSet = None, limit: int = None
    ) -> List[str]:
        raise NotImplementedError

    def info(self) -> dict:
        raise NotImplementedError

    def archive(self, backup_dir: str) -> str:
        raise NotImplementedError


class DefaultStore(Store):

    ENTITY_KEY_PREFIX = "\x00"
    ENTITY_MAP_KEY = "\x00\x01"

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self._trie = None
        self._entity_map = None

    def __len__(self):
        return len(self.entity_map)

    @property
    def exists(self):
        return self.index_path and os.path.exists(self.index_path)

    def load(self):
        if self.exists:
            with open(self.index_path, "rb") as fp:
                data = fp.read()
                try:
                    self._trie = pickle.loads(data)
                except AttributeError:
                    logger.error("Failed to load index: " + self.index_path)

    def commit(self):
        data = pickle.dumps(self._trie)
        utils.safe_write(self.index_path, data)
        return self.index_path

    def reset(self):
        self._entity_map = None
        self._trie = None

    def upsert_entity(self, entity: Entity) -> EID:
        trie_entity_key = self.ENTITY_KEY_PREFIX + entity.key
        entity_id = self.trie.get(trie_entity_key, None)

        if entity_id:
            self.entity_map[entity_id] = entity
        else:
            while entity_id is None:
                timestamp = time.time()
                if entity == self.entity_map.setdefault(timestamp, entity):
                    entity_id = timestamp
                    self.trie.add_word(trie_entity_key, entity_id)

        return entity_id

    def upsert_term(self, term: str, entity_id: EID, label: str):
        term_entities = self.trie.get(term, None)

        if term_entities is None:
            term_entities = TermEntities(entity_id)
            self.trie.add_word(term, term_entities)
        else:
            term_entities.add_term_entity_id(entity_id)

    def get_entity(self, entity_key: str) -> Optional[Entity]:
        trie_entity_key = self.ENTITY_KEY_PREFIX + entity_key
        entity_id = self.trie.get(trie_entity_key, None)
        if entity_id:
            entity = self.entity_map.get(entity_id)
            return entity

    def is_prefix(self, prefix: str, label_set: LabelSet = None) -> bool:
        is_prefix = False

        if label_set:
            label_set = LabelSet.create(label_set)
            for term_entities in self.trie.values(prefix):
                for entity_id in term_entities:
                    entity = self.entity_map.get(entity_id)
                    if label_set.is_allowed(entity.label):
                        is_prefix = True
                        break

        else:
            is_prefix = self.trie.match(prefix)

        return is_prefix

    def get_term_entities(self, term: str) -> TermEntities:
        term_entities = self.trie.get(term, None)
        return term_entities

    def find(self, term: str, label_set: LabelSet = None) -> FindResult:
        term_entities = self.get_term_entities(term)
        entities = ()

        if term_entities:
            label_set = LabelSet.create(label_set)
            for entity_id in term_entities.term_entity_ids:
                entity = self.entity_map.get(entity_id)
                if label_set is None or label_set.is_allowed(entity.label):
                    entities += (entity,)

        return FindResult(term=term, entities=entities)

    def suggest(
        self, term: str, label_set: LabelSet = None, limit: int = None,
    ) -> List[str]:
        suggestions = set()
        count = 0
        limit = limit or 100
        label_set = LabelSet.create(label_set)

        for suggestion, term_entities in self.trie.items(term):
            for entity_id in term_entities:
                entity = self.entity_map.get(entity_id)
                if label_set.is_allowed(entity.label):
                    suggestions.add(suggestion)
                    continue

            count += 1
            if count >= limit:
                break

        return sorted(suggestions)

    def info(self) -> dict:
        info = self.trie.get_stats()
        info["entity_count"] = len(self.entity_map)
        info["path"] = self.index_path
        info["disk_space"] = utils.sizeof(self.index_path)
        info["in_memory"] = utils.sizeof(self.trie)
        info["last_commit"] = utils.file_updated(self.index_path)
        return info

    def archive(self, backup_dir: str):
        update_time = utils.file_updated(self.index_path)
        file_name = os.path.basename(self.index_path)
        file_name += update_time.strftime(".%d-%m-%Y_%I-%M-%S_%p")
        backup_path = os.path.join(backup_dir, file_name)
        os.rename(self.index_path, backup_path)
        return backup_path

    # trie

    @property
    def trie(self) -> ahocorasick.Automaton:
        if self._trie is None:
            self._trie: ahocorasick.Automaton = ahocorasick.Automaton()
        return self._trie

    @property
    def index_path(self):
        if self.root_dir:
            return os.path.join(self.root_dir, "index.db")

    # entities

    @property
    def entity_map(self) -> Dict[float, Entity]:
        if self._entity_map is None:
            self._entity_map = self.trie.get(self.ENTITY_MAP_KEY, None)

            if self._entity_map is None:
                self._entity_map = {}
                self.trie.add_word(self.ENTITY_MAP_KEY, self._entity_map)

        return self._entity_map
