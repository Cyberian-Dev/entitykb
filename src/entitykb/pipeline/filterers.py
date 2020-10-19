from functools import partial
from typing import Optional, Union, Type, List, Iterable

from .model import DocEntity


class Filterer(object):
    @classmethod
    def filter(cls, doc_entities: Iterable[DocEntity]) -> List[DocEntity]:
        raise NotImplementedError


class ExactOnlyFilterer(Filterer):
    """ Only keep entities that are an exact match. """

    @classmethod
    def filter(cls, doc_entities: Iterable[DocEntity]) -> List[DocEntity]:
        it = filter(lambda doc_ent: doc_ent.is_match_exact, doc_entities)
        return list(it)


class KeepLongestByKey(Filterer):
    """ Keeps longest overlapping DocEntity when sharing same key. """

    @classmethod
    def filter_key(cls, doc_entity: DocEntity, offset: int):
        return doc_entity.entity_key, offset

    @classmethod
    def sort_key(cls, doc_entity: DocEntity):
        return doc_entity.sort_order

    @classmethod
    def is_unique(cls, seen: set, doc_entity: DocEntity) -> bool:
        keys = {
            cls.filter_key(doc_entity, offset) for offset in doc_entity.offsets
        }
        is_unique = seen.isdisjoint(keys)
        seen.update(keys)
        return is_unique

    @classmethod
    def filter(cls, doc_entities: Iterable[DocEntity]) -> List[DocEntity]:
        is_unique = partial(cls.is_unique, set())
        sorted_entities = sorted(doc_entities, key=cls.sort_key)
        unique_entities = filter(is_unique, sorted_entities)
        return sorted(unique_entities, key=lambda d: d.offset)


class KeepLongestByLabel(KeepLongestByKey):
    """ Keeps longest overlapping DocEntity when sharing same label. """

    @classmethod
    def filter_key(cls, doc_entity: DocEntity, offset: int):
        return doc_entity.label, offset


class KeepLongestByOffset(KeepLongestByKey):
    """ Keeps only longest overlapping DocEntity. """

    @classmethod
    def filter_key(self, doc_entity: DocEntity, offset: int):
        return offset


FiltererType = Optional[Union[Type[Filterer], Filterer, str]]
