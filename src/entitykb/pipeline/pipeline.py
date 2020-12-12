from dataclasses import dataclass
from typing import Tuple, Iterable

from entitykb import interfaces


@dataclass
class Pipeline(object):
    extractor: interfaces.IExtractor = None
    filterers: Tuple[interfaces.IFilterer, ...] = tuple

    def __call__(self, text: str, labels: Iterable[str]):
        doc = self.extractor.extract_doc(text=text, labels=labels)
        doc.spans = self.filter_spans(doc)
        doc.spans = tuple(doc.spans)
        return doc

    def filter_spans(self, doc):
        spans = doc.spans
        for filterer in self.filterers:
            spans = filterer.filter(spans, doc.tokens)
        return spans
