from typing import List, Tuple, Iterable

from entitykb import Doc, DocToken, Span, create_component

from .handlers import TokenHandler
from .resolvers import Resolver
from .tokenizers import Tokenizer

Labels = Iterable[str]


class Extractor(object):
    def __init__(
        self, tokenizer: Tokenizer, resolvers: Tuple[Resolver, ...],
    ):
        self.tokenizer = tokenizer
        self.resolvers = resolvers

    def __call__(self, text: str, labels: Labels = None) -> Doc:
        return self.extract_doc(text, labels)

    def __repr__(self):
        return self.__class__.__name__

    def extract_doc(self, text: str, labels: Labels = None) -> Doc:
        raise NotImplementedError

    @classmethod
    def create(cls, value=None, **kw):
        return create_component(value, Extractor, DefaultExtractor, **kw)


class DefaultExtractor(Extractor):
    def extract_doc(self, text: str, labels: Labels = None) -> Doc:
        doc = Doc(text=text)
        handlers = self.get_handlers(doc=doc, labels=labels)
        self.process_tokens(doc, handlers, text)
        self.process_spans(doc, handlers, labels)
        return doc

    def get_handlers(self, doc: Doc, labels: Labels) -> List[TokenHandler]:
        handlers: List[TokenHandler] = []
        for resolver in self.resolvers:
            if resolver.is_relevant(labels):
                handler_cls = resolver.get_handler_class()
                handlers.append(handler_cls(doc=doc, resolver=resolver))
        return handlers

    def process_tokens(self, doc, handlers, text):
        offset = 0
        doc_tokens = []
        iter_tokens = self.tokenizer.tokenize(text)
        for token in iter_tokens:
            doc_token = DocToken(doc=doc, token=token, offset=offset)
            doc_tokens.append(doc_token)

            for handler in handlers:
                handler.handle_token(doc_token)

            offset += 1

        doc.tokens = tuple(doc_tokens)
        return doc_tokens

    @classmethod
    def process_spans(cls, doc, handlers, labels):
        spans: List[Span] = []
        for handler in handlers:
            spans += handler.finalize()
        if labels:
            spans = (span for span in spans if span.label in labels)
        doc.spans = tuple(spans)
