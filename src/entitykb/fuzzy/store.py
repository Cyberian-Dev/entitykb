from typing import Optional, Set
from entitykb import DefaultStore, LabelSet, FindResult
from entitykb.store import EID, TermEntities


class TermEditEntities(TermEntities):
    __slots__ = ("term_entity_ids", "edit_entity_ids", "edit_distance")

    def __init__(self, current: TermEntities = None):
        super().__init__(None)
        self.edit_entity_ids: Optional[Set] = None
        self.edit_distance: int = 9
        if current:
            self.term_entity_ids = current.term_entity_ids

    def __str__(self):
        attr = [self.term_entity_ids, self.edit_entity_ids, self.edit_distance]
        attr = ", ".join(map(str, attr))
        return f"<TermEditEntities: {attr}>"

    def __iter__(self):
        if self.term_entity_ids:
            yield from self.term_entity_ids
        if self.edit_entity_ids:
            yield from self.edit_entity_ids

    @classmethod
    def distance(cls, current: TermEntities):
        if isinstance(current, TermEditEntities):
            return current.edit_distance
        else:
            return 0

    @classmethod
    def update(cls, current, entity_id: EID, distance: int) -> TermEntities:
        if isinstance(current, TermEditEntities):
            current.do_add_edit_entity_id(entity_id, distance)

        elif current is None or distance == 0:
            current = TermEditEntities(current)
            current.do_add_edit_entity_id(entity_id, distance)

        return current

    def do_add_edit_entity_id(self, entity_id, distance):
        if not self.edit_entity_ids or entity_id not in self.edit_entity_ids:
            if distance < self.edit_distance:
                self.edit_entity_ids = {entity_id}
                self.edit_distance = distance
            elif distance == self.edit_distance:
                if self.edit_entity_ids:
                    self.edit_entity_ids.add(entity_id)
                else:
                    self.edit_entity_ids = {entity_id}

    def add_term_entity_id(self, entity_id):
        super(TermEditEntities, self).add_term_entity_id(entity_id)
        if self.edit_distance > 0:
            self.edit_distance = 0
            self.edit_entity_ids = None


class FuzzyStore(DefaultStore):
    def upsert_edit(self, edit: str, dist: int, entity_id: EID):
        current = self.trie.get(edit, None)
        updated = TermEditEntities.update(current, entity_id, dist)
        self.trie.add_word(edit, updated)

    def find_edit(self, term: str, label_set: LabelSet = None) -> FindResult:
        reference = self.trie.get(term, None)
        label_set = LabelSet.create(label_set)

        entities = ()
        distance = None

        if reference:
            for entity_id in reference:
                distance = TermEditEntities.distance(reference)
                entity = self.entity_map.get(entity_id)
                if label_set is None or label_set.is_allowed(entity.label):
                    entities += (entity,)

        return FindResult(term=term, entities=entities, distance=distance)
