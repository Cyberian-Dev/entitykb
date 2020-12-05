from entitykb.models import Entity


def test_entity():
    empty = Entity(name="empty")
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
