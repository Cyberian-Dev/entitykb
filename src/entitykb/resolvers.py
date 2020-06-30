from typing import Optional, Union, Type, List

from entitykb import (
    Doc,
    KeepLongestByKey,
    DocEntity,
    DocToken,
    FindResult,
    LabelSet,
    Normalizer,
    Token,
    TokenHandler,
    Tokenizer,
    utils,
    DefaultIndex,
)


class Resolver(object):

    label_set = LabelSet.create()

    def __init__(
        self,
        *,
        tokenizer: Tokenizer,
        normalizer: Normalizer,
        index: DefaultIndex = None,
        **kwargs,
    ):
        self.tokenizer = tokenizer
        self.normalizer = normalizer
        self.index = index

    def resolve(
        self,
        *,
        doc,
        doc_tokens: List[DocToken],
        prefix: Token,
        label_set: LabelSet = None,
    ) -> List[DocEntity]:

        doc_entities = []

        if self.label_set.is_allowed(label_set):
            doc_entities = self.do_resolve(doc, doc_tokens, prefix, label_set)

        return doc_entities

    def do_resolve(
        self, doc, doc_tokens, prefix: str, label_set: LabelSet
    ) -> List[DocEntity]:
        doc_entities = []

        find_result = self.find(term=prefix, label_set=label_set)

        if find_result:
            for (entity_key, entity) in find_result:
                doc_entity = DocEntity(
                    text=prefix,
                    doc=doc,
                    entity_key=entity_key,
                    entity=entity,
                    tokens=doc_tokens,
                )
                doc_entities.append(doc_entity)

        return doc_entities

    def merge_doc_entities(
        self, doc_entities: List[DocEntity]
    ) -> List[DocEntity]:

        doc_entities = KeepLongestByKey().filter(doc_entities)
        self.clean_doc_tokens(doc_entities)
        return doc_entities

    def clean_doc_tokens(self, doc_entities):
        pass

    def find(self, term: str, label_set: LabelSet = None) -> FindResult:
        label_set = self.label_set.intersect(label_set)
        if label_set:
            return self.do_find(term, label_set)

    def do_find(self, term: str, label_set: LabelSet) -> FindResult:
        raise NotImplementedError

    def is_prefix(self, term: str, label_set: LabelSet = None) -> bool:
        label_set = self.label_set.intersect(label_set)
        if label_set:
            return self.do_is_prefix(term, label_set)

    def do_is_prefix(self, term: str, label_set: LabelSet) -> bool:
        raise NotImplementedError

    @classmethod
    def create(cls, resolver: "ResolverType" = None, **kwargs) -> "Resolver":

        if isinstance(resolver, str):
            resolver = utils.instantiate_class_from_name(resolver, **kwargs)

        elif not isinstance(resolver, Resolver):
            resolver = (resolver or DefaultResolver)(**kwargs)

        return resolver

    def create_handler(self, doc: Doc, label_set: LabelSet):
        return TokenHandler(resolver=self, doc=doc, label_set=label_set)


class DefaultResolver(Resolver):
    def do_find(self, term: str, label_set: LabelSet) -> FindResult:
        return self.index.find(term, label_set)

    def do_is_prefix(self, term: str, label_set: LabelSet) -> bool:
        return self.index.is_prefix(term, label_set=label_set)


ResolverType = Optional[Union[Type[Resolver], Resolver, str]]
