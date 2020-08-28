from dataclasses import dataclass
from typing import Tuple, List

from entitykb.config import Config
from entitykb.index import Index, DefaultIndex
from entitykb.model import DocEntity, LabelSet

from . import Tokenizer, Normalizer, Extractor, Filterer, Resolver


@dataclass
class Pipeline(object):
    tokenizer: Tokenizer
    normalizer: Normalizer

    config: Config = None
    index: Index = None
    extractor: Extractor = None
    filterers: Tuple[Filterer, ...] = tuple
    resolvers: Tuple[Resolver, ...] = tuple

    @classmethod
    def create(cls, config: Config):
        tokenizer = Tokenizer.create(config.tokenizer)
        normalizer = Normalizer.create(config.normalizer)

        index = DefaultIndex.create(
            config.index,
            root_dir=config.root_dir,
            tokenizer=tokenizer,
            normalizer=normalizer,
        )

        resolvers = tuple(
            Resolver.create(
                resolver,
                tokenizer=tokenizer,
                normalizer=normalizer,
                index=index,
            )
            for resolver in config.resolvers or [None]
        )
        assert resolvers, f"No resolvers found. ({config})"

        filterers = tuple(
            Filterer.create(filterer) for filterer in config.filterers or []
        )

        extractor = Extractor.create(
            extractor=config.extractor,
            tokenizer=tokenizer,
            resolvers=resolvers,
        )

        pipeline = cls(
            config=config,
            index=index,
            extractor=extractor,
            filterers=filterers,
            normalizer=normalizer,
            resolvers=resolvers,
            tokenizer=tokenizer,
        )

        index.load()

        return pipeline

    # pipeline

    def __call__(self, text: str, label_set: LabelSet = None):
        doc = self.extractor.extract_doc(text=text, label_set=label_set)
        doc.entities = self.filter_entities(doc.entities)
        doc.entities = tuple(doc.entities)
        return doc

    def __len__(self):
        return len(self.index)

    def filter_entities(self, doc_entities: List[DocEntity]):
        for filterer in self.filterers:
            doc_entities = filterer.filter(doc_entities)
        return doc_entities
