from entitykb.models import Doc, DocToken, Entity, Span, Token


def test_entity_create():
    entity = Entity(name="Barack Obama")
    assert entity.name == "Barack Obama"
    assert entity.synonyms == ()
    assert entity.dict() == {
        "key": "Barack Obama|ENTITY",
        "label": "ENTITY",
        "name": "Barack Obama",
        "synonyms": (),
        "data": None,
    }
    assert entity == entity


def test_doc_create():
    doc = Doc(
        text="Hello, Barack Obama!",
        tokens=[
            DocToken(offset=0, token=Token("Hello")),
            DocToken(offset=1, token=Token(",")),
            DocToken(offset=2, token=Token("Barack")),
            DocToken(offset=3, token=Token("Obama")),
            DocToken(offset=4, token=Token("!")),
        ],
    )

    doc.spans = (
        Span(
            text="Barack Obama",
            entity=Entity(name="Barack Obama", label="PRESIDENT"),
            tokens=doc.tokens[2:4],
        ),
        Span(
            text="Obama",
            entity=Entity(name="Barack Obama", label="PERSON"),
            tokens=doc.tokens[3:4],
        ),
    )

    assert doc == doc
    assert len(doc) == 5
    assert str(doc) == "Hello, Barack Obama!"
    assert str(doc[2]) == "Barack"
    assert set(doc.dict().keys()) == {"text", "spans", "tokens"}

    span = doc.spans[0]
    assert span.offsets == (2, 3)
    assert span.offset == 2
    assert span.last_offset == 3
    assert span.dict() == {
        "entity": {
            "key": "Barack Obama|PRESIDENT",
            "label": "PRESIDENT",
            "name": "Barack Obama",
            "synonyms": (),
            "data": None,
        },
        "entity_key": "Barack Obama|PRESIDENT",
        "text": "Barack Obama",
        "tokens": (
            {"offset": 2, "token": "Barack"},
            {"offset": 3, "token": "Obama"},
        ),
    }

    doc_data = doc.dict()
    new_doc = Doc(**doc_data)
    assert new_doc.dict() == doc_data

    assert 2 == len(doc.entities)
