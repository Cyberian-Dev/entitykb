from functools import partial
from typing import List

from entitykb import Span, interfaces


def sort_key(span: Span):
    return (
        -span.num_tokens,
        0 if span.is_exact_name_match else 1,
        0 if span.is_lower_name_match else 1,
        0 if span.is_lower_name_or_exact_synonym_match else 1,
        span.offset,
        span.label,
    )


class ExactNameOnly(interfaces.IFilterer):
    """ Only keep spans that are an exact match. """

    @classmethod
    def filter(cls, spans, tokens) -> List[Span]:
        it = filter(lambda span: span.is_exact_name_match, spans)
        return list(it)


class LowerNameOrExactSynonym(interfaces.IFilterer):
    """ Only keep spans that are an exact match. """

    @classmethod
    def filter(cls, spans, tokens) -> List[Span]:
        it = filter(
            lambda span: span.is_lower_name_or_exact_synonym_match, spans
        )
        return list(it)


class KeepLongestByKey(interfaces.IFilterer):
    """ Keeps longest overlapping span sharing same key. """

    @classmethod
    def filter_key(cls, span: Span, offset: int):
        return span.entity_key, offset

    @classmethod
    def is_unique(cls, max_length: int, seen: set, span: Span) -> bool:
        keys = {cls.filter_key(span, offset) for offset in span.offsets}
        is_unique = seen.isdisjoint(keys)
        seen.update(keys)
        return len(span) == max_length or is_unique

    @classmethod
    def filter(cls, spans, tokens) -> List[Span]:
        if len(spans) > 1:
            sorted_spans = sorted(spans, key=sort_key)
            max_length = len(sorted_spans[0].tokens)
            is_unique = partial(cls.is_unique, max_length, set())
            unique_spans = filter(is_unique, sorted_spans)
            return sorted(unique_spans, key=lambda d: d.offset)

        else:
            return spans


class KeepLongestByLabel(KeepLongestByKey):
    """ Keeps longest overlapping span sharing same label. """

    @classmethod
    def filter_key(cls, span: Span, offset: int):
        return span.label, offset


class KeepLongestByOffset(KeepLongestByKey):
    """ Keeps longest overlapping span. """

    @classmethod
    def filter_key(cls, span: Span, offset: int):
        return offset
