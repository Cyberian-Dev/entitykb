import pytest
from entitykb import (
    Doc,
    DocToken,
    Token,
    Span,
    Entity,
)
from entitykb.pipeline import (
    Pipeline,
    KeepLongestByOffset,
    KeepLongestByKey,
    KeepLongestByLabel,
    ExactNameOnly,
    LowerNameOrExactSynonym,
)


@pytest.fixture()
def doc():
    return Doc(text="a")


@pytest.fixture()
def tokens(doc):
    return [DocToken(doc=doc, token=Token("a"), offset=0)]


@pytest.fixture()
def spans(doc, tokens):
    spans = [
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="A", label="LABEL_0"),
            tokens=tokens,
        ),
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="B", label="LABEL_0"),
            tokens=tokens,
        ),
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="A", label="LABEL_1"),
            tokens=tokens,
        ),
        Span(
            text="a",
            doc=doc,
            entity=Entity(name="C", label="LABEL_0", synonyms=["a"]),
            tokens=tokens,
        ),
    ]
    assert 4 == len(spans)
    return spans


def test_longest_by_key(spans, tokens):
    assert 4 == len(KeepLongestByKey().filter(spans=spans, tokens=tokens))


def test_longest_by_label(spans, tokens):
    assert 2 == len(KeepLongestByLabel().filter(spans=spans, tokens=tokens))


def test_longest_by_offset(spans, tokens):
    assert 1 == len(KeepLongestByOffset().filter(spans=spans, tokens=tokens))


def test_exact_name_only(spans, tokens):
    assert 0 == len(ExactNameOnly().filter(spans=spans, tokens=tokens))


def test_lower_name_or_exact_synonym_only(spans, tokens):
    assert 3 == len(
        LowerNameOrExactSynonym().filter(spans=spans, tokens=tokens)
    )


def test_pipeline(doc, spans, tokens):
    doc.spans = spans
    doc.tokens = tokens
    pipeline = Pipeline(
        filterers=[LowerNameOrExactSynonym(), KeepLongestByLabel()]
    )
    assert 2 == len(pipeline.filter_spans(doc))
