from typing import Iterator

from entitykb import Span, interfaces, Doc


class KeepExactNameOnly(interfaces.IFilterer):
    """ Only keep spans that are an exact match. """

    def is_keep(self, span: Span):
        return span.name == span.text


class RemoveInexactSynonyms(interfaces.IFilterer):
    """ Remove if not exact synonyms. """

    def is_keep(self, span):
        is_keep = span.name and (span.name.lower() == span.text.lower())
        return is_keep or (span.text in span.synonyms)


class DedupeByKeyOffset(interfaces.IFilterer):
    """ Keeps longest overlapping span sharing same key. """

    def __init__(self, doc: Doc = None):
        super().__init__(doc)
        self.seen = set()

    def span_tuple(self, span: Span, offset: int):
        return span.entity_key, offset

    def is_unique(self, span: Span) -> bool:
        keys = {self.span_tuple(span, offset) for offset in span.offsets}
        is_unique = self.seen.isdisjoint(keys)
        self.seen.update(keys)
        return is_unique

    @classmethod
    def sort_key(cls, span: Span):
        return (
            -span.num_tokens,
            span.match_type(),
            span.offset,
            span.label,
        )

    def filter(self, spans: Iterator[Span]) -> Iterator[Span]:
        spans = sorted(spans, key=self.sort_key)
        if len(spans) > 1:
            spans = filter(self.is_unique, spans)
        return spans


class DedupeByLabelOffset(DedupeByKeyOffset):
    """ Keeps longest overlapping span sharing same label. """

    def span_tuple(self, span: Span, offset: int):
        return span.label, offset


class DedupeByOffset(DedupeByKeyOffset):
    """ Keeps longest overlapping spans. """

    def span_tuple(self, span: Span, offset: int):
        return offset
