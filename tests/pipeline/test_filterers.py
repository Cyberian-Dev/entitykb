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
    assert 4 == len(spans)
    return spans


def test_longest_by_key(spans, tokens):
    assert 4 == len(KeepLongestByKey().filter(spans=spans, tokens=tokens))
    assert 1 == len(KeepLongestByKey().filter(spans=spans[:1], tokens=tokens))


def test_longest_by_label(spans, tokens):
    assert 4 == len(KeepLongestByLabel().filter(spans=spans, tokens=tokens))


def test_longest_by_offset(spans, tokens):
    assert 4 == len(KeepLongestByOffset().filter(spans=spans, tokens=tokens))


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
    assert 3 == len(pipeline.filter_spans(doc))
