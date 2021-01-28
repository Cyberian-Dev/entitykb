import pytest

from entitykb import Doc, DocToken, Entity, Span, Token
from entitykb.pipeline import (
    DedupeByKeyOffset,
    DedupeByLabelOffset,
    DedupeByOffset,
    KeepExactNameOnly,
    RemoveInexactSynonyms,
    Pipeline,
)


def count_it(it):
    return len(list(it))


@pytest.fixture()
def doc():
    return Doc(text="a")


@pytest.fixture()
def tokens(doc):
    return [
        DocToken(token=Token("a"), offset=0),
        DocToken(token=Token("b"), offset=1),
    ]


@pytest.fixture()
def spans(doc, tokens):
    spans = [
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="A", label="LABEL_0"),
            tokens=tokens[:1],
        ),
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="B", label="LABEL_0"),
            tokens=tokens[:1],
        ),
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="A", label="LABEL_1"),
            tokens=tokens[:1],
        ),
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="C", label="LABEL_0", synonyms=["a"]),
            tokens=tokens[:1],
        ),
    ]
    assert 4 == count_it(spans)
    return spans


def test_longest_by_key(spans, tokens):
    assert 4 == count_it(DedupeByKeyOffset().filter(spans=spans))
    assert 1 == count_it(DedupeByKeyOffset().filter(spans=spans[:1]))


def test_longest_by_label(spans, tokens):
    assert 2 == count_it(DedupeByLabelOffset().filter(spans=spans))


def test_longest_by_offset(spans, tokens):
    assert 1 == count_it(DedupeByOffset().filter(spans=spans))


def test_exact_name_only(spans, tokens):
    assert 0 == count_it(KeepExactNameOnly().filter(spans=spans))


def test_lower_name_or_exact_synonym_only(spans, tokens):
    assert 3 == count_it(RemoveInexactSynonyms().filter(spans=spans))


def test_pipeline(doc, spans, tokens):
    doc.spans = spans
    doc.tokens = tokens
    pipeline = Pipeline(filterers=(RemoveInexactSynonyms, DedupeByLabelOffset))
    assert 2 == count_it(pipeline.filter_spans(doc))
