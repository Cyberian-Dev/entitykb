from entitykb.models import (
    Entity,
    DocToken,
    DocEntity,
    Doc,
    Token,
)


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

    doc.entities = (
        DocEntity(
            text="Barack Obama",
            entity=Entity(name="Barack Obama", label="PRESIDENT"),
            tokens=doc.tokens[2:4],
        ),
        DocEntity(
            text="Obama",
            entity=Entity(name="Barack Obama", label="PERSON"),
            tokens=doc.tokens[3:4],
        ),
    )

    assert doc == doc
    assert len(doc) == 5
    assert str(doc) == "Hello, Barack Obama!"
    assert str(doc[2]) == "Barack"
    assert set(doc.dict().keys()) == {"text", "entities", "tokens"}

    doc_ent = doc.entities[0]
    assert doc_ent.sort_order == (-2, 0, 0, 2, "PRESIDENT")
    assert doc_ent.offsets == (2, 3)
    assert doc_ent.offset == 2
    assert doc_ent.last_offset == 3
    assert doc_ent.dict() == {
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

    doc_ent = doc.entities[1]
    assert doc_ent.sort_order == (-1, 1, 1, 3, "PERSON")

    assert doc.entities == tuple(sorted(doc.entities))

    doc_data = doc.dict()
    new_doc = Doc(**doc_data)
    assert new_doc.dict() == doc_data
