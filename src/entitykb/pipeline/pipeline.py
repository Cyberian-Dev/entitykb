from dataclasses import dataclass
from typing import Tuple, List, Iterable

from entitykb import BaseKB, Config, get_class_from_name, DocEntity
from . import Tokenizer, Normalizer, Extractor, Filterer, Resolver


@dataclass
class Pipeline(object):
    tokenizer: Tokenizer
    normalizer: Normalizer

    config: Config = None
    kb: BaseKB = None
    extractor: Extractor = None
    filterers: Tuple[Filterer, ...] = tuple
    resolvers: Tuple[Resolver, ...] = tuple

    @classmethod
    def create(cls, kb: BaseKB, config: Config, normalizer: Normalizer):
        tokenizer = Tokenizer.create(config.tokenizer)

        resolvers = tuple(
            Resolver.create(
                resolver, tokenizer=tokenizer, normalizer=normalizer, kb=kb,
            )
            for resolver in config.resolvers or [None]
        )
        assert resolvers, f"No resolvers found. ({config})"

        filterers = config.filterers or []
        filterers = tuple(get_class_from_name(f) for f in filterers)

        extractor = Extractor.create(
            extractor=config.extractor,
            tokenizer=tokenizer,
            resolvers=resolvers,
        )

        pipeline = cls(
            config=config,
            kb=kb,
            extractor=extractor,
            filterers=filterers,
            normalizer=normalizer,
            resolvers=resolvers,
            tokenizer=tokenizer,
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
