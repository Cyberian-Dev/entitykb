from dataclasses import dataclass
from typing import Tuple, Iterable

from entitykb import (
    BaseKB,
    Config,
    PipelineConfig,
    get_class_from_name,
)
from .extractors import Extractor
from .filterers import Filterer
from .normalizers import Normalizer
from .resolvers import Resolver
from .tokenizers import Tokenizer


@dataclass
class Pipeline(object):
    extractor: Extractor = None
    filterers: Tuple[Filterer, ...] = tuple

    @classmethod
    def create(
        cls,
        kb: BaseKB,
        config: Config,
        pipeline: PipelineConfig,
        normalizer: Normalizer,
    ):
        tokenizer = Tokenizer.create(config.tokenizer)

        resolvers = tuple(
            Resolver.create(
                resolver, tokenizer=tokenizer, normalizer=normalizer, kb=kb,
            )
            for resolver in pipeline.resolvers or [None]
        )
        assert resolvers, f"No resolvers found. ({config})"

        filterers = pipeline.filterers or []
        filterers = tuple(get_class_from_name(f) for f in filterers)

        extractor = Extractor.create(
            pipeline.extractor, tokenizer=tokenizer, resolvers=resolvers,
        )

        pipeline = cls(extractor=extractor, filterers=filterers)

        return pipeline

    # pipeline

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
