import datetime

from entitykb import (
    Entity,
    DocToken,
    DocEntity,
    Doc,
    FindResult,
    Token,
)
from entitykb.date import Date


def test_entity_create():
    entity = Entity(name="Barack Obama")
    assert entity.name == "Barack Obama"
    assert entity.synonyms == ()
    assert entity.dict() == {
        "label": "ENTITY",
        "meta": None,
        "name": "Barack Obama",
        "key": "Barack Obama|ENTITY",
        "synonyms": (),
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
        )
    ]

    assert doc == doc
    assert doc.tokens == tokens
    assert len(doc) == 5
    assert str(doc) == "Hello, Barack Obama!"
    assert str(doc[2]) == "Barack"
    assert set(doc.dict().keys()) == {"text", "entities", "tokens"}

    doc_ent = doc.entities[0]
    assert doc_ent.doc == doc
    assert doc_ent.sort_order == (-2, False, -100, 0, 0, 0, 2, "PRESIDENT")
    assert doc_ent.offsets == (2, 3)
    assert doc_ent.dict() == {
        "correction": None,
        "entity": {
            "key": "Barack Obama|PRESIDENT",
            "label": "PRESIDENT",
            "meta": None,
            "name": "Barack Obama",
            "synonyms": (),
        },
        "entity_key": "Barack Obama|PRESIDENT",
        "text": "Barack Obama",
        "tokens": [
            {"offset": 2, "token": "Barack"},
            {"offset": 3, "token": "Obama"},
        ],
    }


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


def test_default_label():
    entity = Entity(name="Barack Obama")
    assert entity.label == "ENTITY"

    class President(Entity):
        pass

    entity = President(name="Barack Obama")
    assert entity.label == "PRESIDENT"


def test_from_dict():
    d = dict(name="2000-01-02", year=2000, month=1, day=2)
    entity = Entity.from_dict(d)
    assert entity.meta == dict(year=2000, month=1, day=2)
    assert repr(entity) == "2000-01-02|ENTITY"

    date = Date.from_dict(d)
    assert date.year == 2000
    assert date.month == 1
    assert date.day == 2
    assert date.meta is None
    assert repr(date) == "2000-01-02|DATE"

    d = dict(name="MET", synonyms="AUTS9||HGFR", ignored=None)
    gene = Entity.from_dict(d, mv_keys={"synonyms"}, mv_sep="||")
    assert gene.name == "MET"
    assert gene.synonyms == ("AUTS9", "HGFR")
    assert gene.meta is None


def test_date():
    date = Date(year=2001, month=2, day=3)
    assert date.name == "2001-02-03"
    assert date.as_date == datetime.date(2001, 2, 3)
    assert date.dict() == dict(
        name="2001-02-03",
        key="2001-02-03|DATE",
        year=2001,
        month=2,
        day=3,
        label="DATE",
        meta=None,
        synonyms=(),
    )
