import pytest

from entitykb import Entity, interfaces
from entitykb.contrib.date import Date, DateResolver
from entitykb.pipeline import (
    DefaultExtractor,
    TermResolver,
    WhitespaceTokenizer,
)

the_the = Entity(name="The The", label="BAND")


@pytest.fixture(scope="function")
def extractor(kb, apple, google, amazon, microsoft):
    tokenizer = WhitespaceTokenizer()
    resolver = TermResolver(kb=kb)

    for entity in (apple, google, amazon, microsoft, the_the):
        kb.save_node(entity)
    kb.reindex()

    resolvers = (resolver, DateResolver(kb=kb))
    extractor = DefaultExtractor(tokenizer=tokenizer, resolvers=resolvers)
    return extractor


def test_extract_default_classes(
    extractor: interfaces.IExtractor, apple, google, amazon, microsoft
):
    text = "She invested in AAPL, google, Amazon, and microsoft"

    # noinspection PyCallingNonCallable
    doc = extractor(text)
    assert len(doc.spans) == 4

    assert doc.spans[0].entity_key == apple.key
    assert doc.spans[1].entity_key == google.key
    assert doc.spans[2].entity_key == amazon.key
    assert doc.spans[3].entity_key == microsoft.key

    assert doc.spans[0].text == "AAPL"
    assert doc.spans[1].text == "google"
    assert doc.spans[2].text == "Amazon"
    assert doc.spans[3].text == "microsoft"


def test_extract_multi_token(
    extractor: interfaces.IExtractor, apple, google, amazon, microsoft
):
    text = (
        "She invested in Apple, Inc., Google, Inc., Amazon, Inc., "
        "and The The Microsoft Corporation. Plus more AAPL and MSFT."
    )
    doc = extractor(text)
    assert len(doc.spans) == 8, f"Incorrect: {doc.spans}"

    assert doc.spans[0].text == "Apple, Inc."
    assert doc.spans[1].text == "Google, Inc."
    assert doc.spans[2].text == "Amazon, Inc."
    assert doc.spans[3].text == "The The"
    assert doc.spans[4].text == "The Microsoft Corporation"
    assert doc.spans[5].text == "Microsoft Corporation"
    assert doc.spans[6].text == "AAPL"
    assert doc.spans[7].text == "MSFT"

    doc = extractor(text, ("COMPANY", "BAND"))
    assert len(doc.spans) == 8

    doc = extractor(text, ("BAND",))
    assert len(doc.spans) == 1

    doc = extractor(text, ("COMPANY",))
    assert len(doc.spans) == 7


def test_extract_with_date(extractor: interfaces.IExtractor, apple):
    text = "Apple, Inc. was founded on April 1, 1976."
    doc = extractor(text)
    assert len(doc.spans) == 2
    assert doc.spans[0].entity_key == "Apple, Inc.|COMPANY"
    assert doc.spans[1].entity == Date(
        year=1976, month=4, day=1, synonyms=("April 1, 1976",)
    )
