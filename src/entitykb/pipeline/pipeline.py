from dataclasses import dataclass
from typing import Tuple, List, Iterable

from entitykb import (
    BaseKB,
    Config,
    PipelineConfig,
    DocEntity,
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
    resolvers: Tuple[Resolver, ...] = tuple

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

        pipeline = cls(
            extractor=extractor, filterers=filterers, resolvers=resolvers,
        )

        return pipeline

    # pipeline

    def __call__(self, text: str, labels: Iterable[str]):
        doc = self.extractor.extract_doc(text=text, labels=labels)
        doc.entities = self.filter_entities(doc.entities)
        doc.entities = tuple(doc.entities)
        return doc

    def filter_entities(self, doc_entities: List[DocEntity]):
        for filterer in self.filterers:
            doc_entities = filterer.filter(doc_entities)
        return doc_entities
