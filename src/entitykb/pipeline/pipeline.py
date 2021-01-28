from dataclasses import dataclass
from typing import Tuple, Iterable, Type

from entitykb import interfaces


@dataclass
class Pipeline(object):
    extractor: interfaces.IExtractor = None
    filterers: Tuple[Type[interfaces.IFilterer], ...] = tuple

    def __call__(self, text: str, labels: Iterable[str]):
        doc = self.extractor.extract_doc(text=text, labels=labels)
        doc.spans = self.filter_spans(doc)
        return doc

    def filter_spans(self, doc):
        spans = iter(doc.spans)
        for filterer_cls in self.filterers:
            filterer = filterer_cls(doc)
            spans = filterer.filter(spans)
        spans = sorted(spans, key=lambda span: span.offset)
        return tuple(spans)
