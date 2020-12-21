from typing import List

from entitykb import Doc, DocToken, Span, create_component, interfaces, istr
from .handlers import TokenHandler


class DefaultExtractor(interfaces.IExtractor):
    def extract_doc(self, text: str, labels: istr = None) -> Doc:
        doc = Doc(text=text)
        handlers = self.get_handlers(doc=doc, labels=labels)
        self.process_tokens(doc, handlers, text)
        self.process_spans(doc, handlers, labels)
        return doc

    def get_handlers(self, doc: Doc, labels: istr) -> List[TokenHandler]:
        handlers: List[TokenHandler] = []
        for resolver in self.resolvers:
            if resolver.is_relevant(labels):
                handler_cls = resolver.get_handler_class()
                handler = create_component(
                    value=handler_cls,
                    default_cls=TokenHandler,
                    doc=doc,
                    resolver=resolver,
                    labels=labels,
                )
                handlers.append(handler)
        return handlers

    def process_tokens(self, doc, handlers, text):
        offset = 0
        doc_tokens = []
        iter_tokens = self.tokenizer.tokenize(text)
        for token in iter_tokens:
            doc_token = DocToken(token=token, offset=offset)
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
            spans = list((span for span in spans if span.label in labels))
        doc.spans = tuple(spans)
