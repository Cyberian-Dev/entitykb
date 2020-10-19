import pytest
from entitykb import (
    Doc,
    DocToken,
    Token,
    DocEntity,
    Entity,
)
from entitykb.pipeline import (
    Pipeline,
    KeepLongestByOffset,
    KeepLongestByKey,
    KeepLongestByLabel,
    ExactOnlyFilterer,
)


@pytest.fixture()
def doc_entities():
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
    return doc_entities


def test_longest_filters(doc_entities):
    doc_entities = KeepLongestByKey().filter(doc_entities=doc_entities)
    assert 3 == len(doc_entities)

    doc_entities = KeepLongestByLabel().filter(doc_entities=doc_entities)
    assert 2 == len(doc_entities)

    doc_entities = KeepLongestByOffset().filter(doc_entities=doc_entities)
    assert 1 == len(doc_entities)


def test_pipeline_filter_entities(doc_entities):
    pipeline = Pipeline(
        tokenizer=None, normalizer=None, filterers=[ExactOnlyFilterer()],
    )
    assert 3 == len(pipeline.filter_entities(doc_entities))
