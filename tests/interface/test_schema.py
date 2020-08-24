from dataclasses import asdict

from entitykb.interface.schema import Entity


def test_entity_create():
    entity = Entity(
        key="Barack Obama|ENTITY",
        name="Barack Obama",
        synonyms=(),
        label="ENTITY",
        meta={},
    )
    assert entity.name == "Barack Obama"
    assert not entity.synonyms
    assert entity.label == "ENTITY"
    assert entity.key == "Barack Obama|ENTITY"
    assert asdict(entity) == {
        "label": "ENTITY",
        "meta": {},
        "name": "Barack Obama",
        "key": "Barack Obama|ENTITY",
        "synonyms": [],
    }
