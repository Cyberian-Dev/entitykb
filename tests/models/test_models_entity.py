from msgpack import packb, unpackb

from entitykb.models import Entity
from pydantic.json import pydantic_encoder


def test_entity():
    empty = Entity(name="empty", synonyms=None)
    assert empty.dict() == dict(
        name="empty",
        synonyms=tuple(),
        key="empty|ENTITY",
        label="ENTITY",
        data=None,
    )
    assert empty.terms == ("empty",)

    entity = Entity(name="GenomOncology", label="COMPANY", synonyms="GO")
    assert entity.dict() == dict(
        name="GenomOncology",
        synonyms=("GO",),
        key="GenomOncology|COMPANY",
        label="COMPANY",
        data=None,
    )
    assert entity.terms == ("GenomOncology", "GO")


def test_custom_entity_class(apple):
    assert apple.label == "COMPANY"


def test_sort_entities(apple, google):
    assert [apple, google] == sorted((google, apple))
    assert [apple, google] == sorted((apple, google))


def test_pack_unpack(apple):
    data = packb(apple, default=pydantic_encoder)
    assert isinstance(data, bytes)
    entity = unpackb(data, object_hook=Entity.create)
    assert entity == apple
