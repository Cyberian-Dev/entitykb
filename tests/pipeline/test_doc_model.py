from entitykb.models import (
    Entity,
    DocToken,
    DocEntity,
    Doc,
    FindResult,
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
    doc = Doc(text="Hello, Barack Obama!")

    tokens = (
        DocToken(doc=doc, offset=0, token=Token("Hello")),
        DocToken(doc=doc, offset=1, token=Token(",")),
        DocToken(doc=doc, offset=2, token=Token("Barack")),
        DocToken(doc=doc, offset=3, token=Token("Obama")),
        DocToken(doc=doc, offset=4, token=Token("!")),
    )
    doc.tokens = tokens
    doc.entities = [
        DocEntity(
            doc=doc,
            text="Barack Obama",
            entity=Entity(name="Barack Obama", label="PRESIDENT"),
            tokens=tokens[2:4],
        ),
        DocEntity(
            doc=doc,
            text="Obama",
            entity=Entity(name="Barack Obama", label="PERSON"),
            tokens=tokens[3:4],
        ),
    ]

    assert doc == doc
    assert doc.tokens == tokens
    assert len(doc) == 5
    assert str(doc) == "Hello, Barack Obama!"
    assert str(doc[2]) == "Barack"
    assert set(doc.dict().keys()) == {"text", "entities", "tokens"}

    doc_ent = doc.entities[0]
    assert doc_ent.doc == doc
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
        "tokens": [
            {"offset": 2, "token": "Barack"},
            {"offset": 3, "token": "Obama"},
        ],
    }

    doc_ent = doc.entities[1]
    assert doc_ent.sort_order == (-1, 1, 1, 3, "PERSON")

    assert doc.entities == sorted(doc.entities)

    doc_data = doc.dict()
    new_doc = Doc(**doc_data)
    assert new_doc.dict() == doc_data


def test_equality_and_hash_using_synonyms():
    gene_1 = Entity(name="MET", label="GENE", synonyms=("AUTS9", "HGFR"))
    gene_2 = Entity(name="MET", label="GENE", synonyms=("HGFR", "AUTS9"))
    gene_3 = Entity(name="MET", label="GENE", synonyms=("HGFR",))

    assert hash(gene_1) == hash(gene_2)
    assert hash(gene_1) == hash(gene_3)

    assert gene_1 == gene_2
    assert gene_1 == gene_3


def test_create_find_result():
    result = FindResult(
        term="aaa", entities=[Entity(name="AAA", label="ENTITY")]
    )
    assert hash(result)
    assert str(result) == "aaa [AAA|ENTITY]"
    assert len(result) == 1
