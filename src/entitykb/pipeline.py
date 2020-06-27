from dataclasses import dataclass
from typing import Tuple, List

import entitykb


@dataclass
class Pipeline(object):
    tokenizer: entitykb.Tokenizer
    normalizer: entitykb.Normalizer

    config: entitykb.Config = None
    index: entitykb.DefaultIndex = None
    extractor: entitykb.Extractor = None
    filterers: Tuple[entitykb.Filterer, ...] = tuple
    resolvers: Tuple[entitykb.Resolver, ...] = tuple

    @classmethod
    def create(cls, config: entitykb.Config):
        tokenizer = entitykb.Tokenizer.create(config.tokenizer)
        normalizer = entitykb.Normalizer.create(config.normalizer)

        index = entitykb.DefaultIndex.create(
            config.index,
            root_dir=config.root_dir,
            tokenizer=tokenizer,
            normalizer=normalizer,
        )

        resolvers = tuple(
            entitykb.Resolver.create(
                resolver,
                tokenizer=tokenizer,
                normalizer=normalizer,
                index=index,
            )
            for resolver in config.resolvers
        )
        assert resolvers, f"No resolvers found. ({config})"

        filterers = tuple(
            entitykb.Filterer.create(filterer) for filterer in config.filterers
        )

        extractor = entitykb.Extractor.create(
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

        pipeline.reload()

        return pipeline

    # pipeline

    def __call__(self, text: str, label_set: entitykb.LabelSet = None):
        doc = self.extractor.extract_doc(text=text, label_set=label_set)
        doc.entities = self.filter_entities(doc.entities)
        doc.entities = tuple(doc.entities)
        return doc

    def __len__(self):
        return len(self.index)

    def filter_entities(self, doc_entities: List[entitykb.DocEntity]):
        for filterer in self.filterers:
            doc_entities = filterer.filter(doc_entities)
        return doc_entities

    # indices

    def reload(self):
        self.index.load()

    def reset(self):
        self.index.reset()

    def commit(self):
        self.index.commit()

    # entities

    def add(self, *entities: entitykb.Entity):
        for entity in entities:
            self.index.add(entity)
