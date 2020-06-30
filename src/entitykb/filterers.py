from typing import Optional, Union, Type, List, Iterable
from functools import partial

from .model import DocEntity
from .utils import instantiate_class_from_name


class Filterer(object):
    def filter(self, doc_entities: Iterable[DocEntity]) -> List[DocEntity]:
        raise NotImplementedError

    @classmethod
    def create(cls, filterer: "FiltererType" = None) -> "Filterer":
        if isinstance(filterer, str):
            filterer = instantiate_class_from_name(filterer)
        elif not isinstance(filterer, Filterer):
            filterer = (filterer or cls)()

        return filterer


class ExactOnlyFilterer(Filterer):
    def filter(self, doc_entities: Iterable[DocEntity]) -> List[DocEntity]:
        it = filter(lambda doc_ent: doc_ent.is_match_exact, doc_entities)
        return list(it)


class BaseUniqueFilterer(Filterer):
    def filter_key(self, doc_entity: DocEntity, offset: int):
        raise NotImplementedError

    def sort_key(self, doc_entity: DocEntity):
        return doc_entity.sort_order

    def is_unique(self, seen: set, doc_entity: DocEntity) -> bool:
        keys = {
            self.filter_key(doc_entity, offset)
            for offset in doc_entity.offsets
        }
        is_unique = seen.isdisjoint(keys)
        seen.update(keys)
        return is_unique

    def filter(self, doc_entities: Iterable[DocEntity]) -> List[DocEntity]:
        is_unique = partial(self.is_unique, set())

        sorted_entities = sorted(doc_entities, key=self.sort_key)
        unique_entities = filter(is_unique, sorted_entities)

        return sorted(unique_entities, key=lambda d: d.offset)


class KeepLongestByKey(BaseUniqueFilterer):
    """ Keeps longest overlapping DocEntity when sharing same entity key. """

    def filter_key(self, doc_entity: DocEntity, offset: int):
        return doc_entity.entity_key, offset


class KeepLongestByLabel(BaseUniqueFilterer):
    """ Keeps longest overlapping DocEntity when sharing same label. """

    def filter_key(self, doc_entity: DocEntity, offset: int):
        return doc_entity.label, offset


class KeepLongestOnly(BaseUniqueFilterer):
    """ Keeps only longest overlapping DocEntity. """

    def filter_key(self, doc_entity: DocEntity, offset: int):
        return offset


FiltererType = Optional[Union[Type[Filterer], Filterer, str]]
