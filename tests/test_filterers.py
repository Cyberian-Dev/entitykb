from entitykb import (
    Doc,
    DocToken,
    Token,
    MergeEntityFilterer,
    DocEntity,
    ExactOnlyFilterer,
    Filterer,
)


def test_construct():
    assert isinstance(
        Filterer.create("entitykb.ExactOnlyFilterer"), ExactOnlyFilterer
    )
    assert isinstance(MergeEntityFilterer.create(), MergeEntityFilterer)

    filterer = MergeEntityFilterer()
    assert Filterer.create(filterer) == filterer


def test_merge_filterer():
    doc = Doc(text="a")
    tokens = [DocToken(doc=doc, token=Token("a"), offset=0)]

    doc_entities = [
        DocEntity(text="0", doc=doc, entity_key="0|A", tokens=tokens),
        DocEntity(text="0", doc=doc, entity_key="0|A", tokens=tokens),
        DocEntity(text="0", doc=doc, entity_key="1|A", tokens=tokens),
        DocEntity(text="0", doc=doc, entity_key="0|B", tokens=tokens),
    ]
    assert 4 == len(doc_entities)

    doc_entities = MergeEntityFilterer().filter(doc_entities=doc_entities)
    assert 3 == len(doc_entities)
