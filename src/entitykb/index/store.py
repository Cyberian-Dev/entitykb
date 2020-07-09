import os
import pickle
from typing import List, Optional, Any, Set

import ahocorasick

from entitykb import Entity, Relationship, FindResult, LabelSet, utils, logger
from . import Graph

EID = Any


class TermEntities(object):
    __slots__ = ("term_entity_ids",)

    def __init__(self, entity_id: EID):
        self.term_entity_ids: Set = set()
        if entity_id is not None:
            self.term_entity_ids.add(entity_id)

    def __repr__(self):
        return f"<TermEntities: {self.term_entity_ids}>"

    def __iter__(self):
        if self.term_entity_ids:
            yield from self.term_entity_ids

    def add_term_entity_id(self, entity_id):
        if entity_id not in self.term_entity_ids:
            self.term_entity_ids.add(entity_id)


class Store(object):
    max_backups = 5

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

    def add_entity(self, entity: Entity) -> EID:
        raise NotImplementedError

    def add_relationship(self, relationship: Relationship):
        raise NotImplementedError

    def add_term(self, term: str, entity_id: EID):
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

    def archive(self):
        raise NotImplementedError


class DefaultStore(Store):
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self._trie = None
        self._graph = None

    def __len__(self):
        return len(self.graph)

    @property
    def trie(self) -> ahocorasick.Automaton:
        if self._trie is None:
            self._trie: ahocorasick.Automaton = ahocorasick.Automaton()
        return self._trie

    @property
    def graph(self) -> Graph:
        if self._graph is None:
            self._graph: Graph = Graph()
        return self._graph

    def add_entity(self, entity: Entity) -> EID:
        return self.graph.add_entity(entity)

    def add_relationship(self, relationship: Relationship):
        return self.graph.add_relationship(relationship)

    def add_term(self, term: str, entity_id: EID):
        term_entities = self.trie.get(term, None)

        if term_entities is None:
            term_entities = TermEntities(entity_id)
            self.trie.add_word(term, term_entities)
        else:
            term_entities.add_term_entity_id(entity_id)

    def get_entity(self, entity_key: str) -> Optional[Entity]:
        entity = self.graph.get_entity(entity_key)
        return entity

    def is_prefix(self, prefix: str, label_set: LabelSet = None) -> bool:
        is_prefix = False

        if label_set:
            label_set = LabelSet.create(label_set)
            for term_entities in self.trie.values(prefix):
                for entity_id in term_entities:
                    entity = self.graph.get_entity(entity_id)
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
                entity = self.graph.get_entity(entity_id)
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
                entity = self.graph.get_entity(entity_id)
                if label_set.is_allowed(entity.label):
                    suggestions.add(suggestion)
                    continue

            count += 1
            if count >= limit:
                break

        return sorted(suggestions)

    def info(self) -> dict:
        info = self.trie.get_stats()
        info["entity_count"] = len(self.graph)
        info["path"] = self.index_path
        info["disk_space"] = utils.sizeof(self.index_path)
        info["in_memory"] = utils.sizeof(self.trie)
        info["last_commit"] = utils.file_updated(self.index_path)
        return info

    # trie
    @property
    def index_path(self):
        if self.root_dir:
            return os.path.join(self.root_dir, "index.db")

    @property
    def exists(self):
        return self.index_path and os.path.exists(self.index_path)

    def load(self):
        if self.exists:
            with open(self.index_path, "rb") as fp:
                data = fp.read()
                try:
                    self._trie, self._graph = pickle.loads(data)
                except AttributeError:
                    logger.error("Failed to load index: " + self.index_path)

    def commit(self):
        data = pickle.dumps((self._trie, self._graph))
        utils.safe_write(self.index_path, data)

    def reset(self):
        self._graph = None
        self._trie = None

    # backups

    @property
    def backup_dir(self):
        backup_dir = os.path.join(self.root_dir, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def archive(self):
        if self.exists and self.max_backups:
            path = self.index_path
            update_time = utils.file_updated(path)
            file_name = os.path.basename(path)
            file_name += update_time.strftime(".%d-%m-%Y_%I-%M-%S_%p")
            backup_path = os.path.join(self.backup_dir, file_name)
            os.rename(path, backup_path)

            self.clean_backups()

    def clean_backups(self) -> Optional[str]:
        paths = [f"{self.backup_dir}/{x}" for x in os.listdir(self.backup_dir)]
        paths = sorted(paths, key=os.path.getctime)

        if len(paths) >= self.max_backups:
            oldest = paths[0]
            os.remove(oldest)
            return oldest
