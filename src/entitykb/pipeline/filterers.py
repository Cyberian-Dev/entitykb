from functools import partial
from typing import Optional, Union, Type, List

from entitykb.models import Span


class Filterer(object):
    @classmethod
    def filter(cls, spans, tokens) -> List[Span]:
        raise NotImplementedError


class ExactOnlyFilterer(Filterer):
    """ Only keep spans that are an exact match. """

    @classmethod
    def filter(cls, spans, tokens) -> List[Span]:
        it = filter(lambda span: span.is_match_exact, spans)
        return list(it)


class KeepLongestByKey(Filterer):
    """ Keeps longest overlapping span sharing same key. """

    @classmethod
    def filter_key(cls, span: Span, offset: int):
        return span.entity_key, offset

    @classmethod
    def sort_key(cls, span: Span):
        return span.sort_order

    @classmethod
    def is_unique(cls, seen: set, span: Span) -> bool:
        keys = {cls.filter_key(span, offset) for offset in span.offsets}
        is_unique = seen.isdisjoint(keys)
        seen.update(keys)
        return is_unique

    @classmethod
    def filter(cls, spans, tokens) -> List[Span]:
        is_unique = partial(cls.is_unique, set())
        sorted_spans = sorted(spans, key=cls.sort_key)
        unique_spans = filter(is_unique, sorted_spans)
        return sorted(unique_spans, key=lambda d: d.offset)


class KeepLongestByLabel(KeepLongestByKey):
    """ Keeps longest overlapping span sharing same label. """

    @classmethod
    def filter_key(cls, span: Span, offset: int):
        return span.label, offset


class KeepLongestByOffset(KeepLongestByKey):
    """ Keeps longest overlapping span. """

    @classmethod
    def filter_key(self, span: Span, offset: int):
        return offset


FiltererType = Optional[Union[Type[Filterer], Filterer, str]]
