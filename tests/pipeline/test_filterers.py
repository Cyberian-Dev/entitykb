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
    ExactOnlyFilterer,
)


@pytest.fixture()
def spans():
    doc = Doc(text="a")
    tokens = [DocToken(doc=doc, token=Token("a"), offset=0)]

    spans = [
        Span(
            text="0",
            doc=doc,
            entity=Entity(name="0", label="A"),
            tokens=tokens,
        ),
        Span(
            text="0",
            doc=doc,
            entity=Entity(name="0", label="A"),
            tokens=tokens,
        ),
        Span(
            text="0",
            doc=doc,
            entity=Entity(name="1", label="A"),
            tokens=tokens,
        ),
        Span(
            text="0",
            doc=doc,
            entity=Entity(name="0", label="B"),
            tokens=tokens,
        ),
    ]
    assert 4 == len(spans)
    return spans


def test_longest_filters(spans):
    spans = KeepLongestByKey().filter(spans=spans)
    assert 3 == len(spans)

    spans = KeepLongestByLabel().filter(spans=spans)
    assert 2 == len(spans)

    spans = KeepLongestByOffset().filter(spans=spans)
    assert 1 == len(spans)


def test_pipeline_filter_spans(spans):
    pipeline = Pipeline(filterers=[ExactOnlyFilterer()])
    assert 3 == len(pipeline.filter_spans(spans))
