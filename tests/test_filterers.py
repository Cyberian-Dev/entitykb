from entitykb import (
    Doc,
    DocToken,
    Token,
    KeepLongestOnly,
    KeepLongestByKey,
    KeepLongestByLabel,
    DocEntity,
    ExactOnlyFilterer,
    Filterer,
    Entity,
)


def test_construct():
    assert isinstance(
        Filterer.create("entitykb.ExactOnlyFilterer"), ExactOnlyFilterer
    )
    assert isinstance(KeepLongestByKey.create(), KeepLongestByKey)

    filterer = KeepLongestByKey()
    assert Filterer.create(filterer) == filterer


def test_merge_filterer():
    doc = Doc(text="a")
    tokens = [DocToken(doc=doc, token=Token("a"), offset=0)]

    doc_entities = [
        DocEntity(
            text="0",
            doc=doc,
            entity=Entity(name="0", label="A"),
            tokens=tokens,
        ),
        DocEntity(
            text="0",
            doc=doc,
            entity=Entity(name="0", label="A"),
            tokens=tokens,
        ),
        DocEntity(
            text="0",
            doc=doc,
            entity=Entity(name="1", label="A"),
            tokens=tokens,
        ),
        DocEntity(
            text="0",
            doc=doc,
            entity=Entity(name="0", label="B"),
            tokens=tokens,
        ),
    ]
    assert 4 == len(doc_entities)

    doc_entities = KeepLongestByKey().filter(doc_entities=doc_entities)
    assert 3 == len(doc_entities)

    doc_entities = KeepLongestByLabel().filter(doc_entities=doc_entities)
    assert 2 == len(doc_entities)

    doc_entities = KeepLongestOnly().filter(doc_entities=doc_entities)
    assert 1 == len(doc_entities)
