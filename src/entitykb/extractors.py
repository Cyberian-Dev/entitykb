from typing import Optional, Union, Type, List, Tuple

from . import (
    Doc,
    DocToken,
    DocEntity,
    LabelSet,
    Resolver,
    Tokenizer,
    utils,
    TokenHandler,
)


class Extractor(object):
    def __init__(
        self, tokenizer: Tokenizer, resolvers: Tuple[Resolver, ...],
    ):
        self.tokenizer = tokenizer
        self.resolvers = resolvers

    def __call__(self, text: str, label_set: LabelSet = None) -> Doc:
        return self.extract_doc(text, label_set)

    def extract_doc(self, text: str, label_set: LabelSet = None) -> Doc:
        raise NotImplementedError

    @classmethod
    def create(cls, extractor: "ExtractorType" = None, **kwargs):
        if isinstance(extractor, str):
            extractor = utils.instantiate_class_from_name(extractor, **kwargs)
        elif not isinstance(extractor, Extractor):
            extractor = (extractor or DefaultExtractor)(**kwargs)
        return extractor


class DefaultExtractor(Extractor):
    def extract_doc(self, text: str, label_set: LabelSet = None) -> Doc:
        doc = Doc(text=text)

        iter_tokens = self.tokenizer.tokenize(text)
        doc_tokens = []
        handlers: List[TokenHandler] = [
            resolver.create_handler(doc=doc, label_set=label_set)
            for resolver in self.resolvers
        ]

        offset = 0
        for token in iter_tokens:
            doc_token = DocToken(doc=doc, token=token, offset=offset)
            doc_tokens.append(doc_token)

            for handler in handlers:
                handler.handle_token(doc_token)

            offset += 1

        doc_entities: List[DocEntity] = []
        for handler in handlers:
            doc_entities += handler.get_doc_entities()

        doc.tokens = tuple(doc_tokens)
        doc.entities = tuple(doc_entities)

        return doc


ExtractorType = Optional[Union[Type[Extractor], Extractor, str]]
