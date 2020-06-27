import pytest

from entitykb import (
    DefaultResolver,
    DefaultTokenizer,
    DefaultNormalizer,
    Entity,
    Extractor,
    Pipeline,
    DefaultIndex,
)
from entitykb.date import DateResolver, Date

the_the = Entity(name="The The", label="BAND")


@pytest.fixture(scope="function")
def extractor(apple, google, amazon, microsoft):
    tokenizer = DefaultTokenizer()
    normalizer = DefaultNormalizer()

    index = DefaultIndex(tokenizer=tokenizer, normalizer=normalizer)

    resolver = DefaultResolver(
        name="default",
        tokenizer=tokenizer,
        normalizer=normalizer,
        index=index,
    )

    pipeline = Pipeline(
        tokenizer=tokenizer,
        normalizer=normalizer,
        index=index,
        resolvers=(resolver,),
    )

    pipeline.add(apple, google, amazon, microsoft, the_the)

    resolvers = (
        resolver,
        DateResolver(tokenizer=tokenizer, normalizer=normalizer, index=index),
    )
    extractor = Extractor.create(tokenizer=tokenizer, resolvers=resolvers,)
    return extractor


def test_extract_default_classes(
    extractor: Extractor, apple, google, amazon, microsoft
):
    text = "She invested in AAPL, google, Amazon, and microsoft"

    # noinspection PyCallingNonCallable
    doc = extractor(text)
    assert len(doc.entities) == 4

    assert doc.entities[0].entity_key == apple.key
    assert doc.entities[1].entity_key == google.key
    assert doc.entities[2].entity_key == amazon.key
    assert doc.entities[3].entity_key == microsoft.key

    assert doc.entities[0].text == "AAPL"
    assert doc.entities[1].text == "google"
    assert doc.entities[2].text == "Amazon"
    assert doc.entities[3].text == "microsoft"


def test_extract_multi_token(
    extractor: Extractor, apple, google, amazon, microsoft
):
    text = (
        "She invested in Apple, Inc., Google, Inc., Amazon, Inc., "
        "and The The Microsoft Corporation. Plus more AAPL and MSFT."
    )
    doc = extractor(text)
    assert len(doc.entities) == 7

    assert doc.entities[0].text == "Apple, Inc."
    assert doc.entities[1].text == "Google, Inc."
    assert doc.entities[2].text == "Amazon, Inc."
    assert doc.entities[3].text == "The The"
    assert doc.entities[4].text == "The Microsoft Corporation"
    assert doc.entities[5].text == "AAPL"
    assert doc.entities[6].text == "MSFT"

    doc = extractor(text, ("COMPANY",))
    assert len(doc.entities) == 6

    doc = extractor(text, ("COMPANY", "BAND"))
    assert len(doc.entities) == 7

    doc = extractor(text, ("BAND",))
    assert len(doc.entities) == 1


def test_extract_with_date(extractor: Extractor, apple):
    text = "Apple, Inc. was founded on April 1, 1976."
    doc = extractor(text)
    assert len(doc.entities) == 2
    assert doc.entities[0].entity_key == "Apple, Inc.|COMPANY"
    assert doc.entities[1].entity == Date(year=1976, month=4, day=1)
