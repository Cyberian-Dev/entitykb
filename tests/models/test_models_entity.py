from entitykb.models import Entity, Node


def test_entity():
    empty = Entity(name="empty")
    assert empty.dict() == dict(
        name="empty",
        synonyms=tuple(),
        key="empty|ENTITY",
        label="ENTITY",
        attrs={},
    )
    assert empty.terms == ("empty",)

    entity = Entity(name="GenomOncology", label="COMPANY", synonyms=("GO",))
    assert entity.dict() == dict(
        name="GenomOncology",
        synonyms=("GO",),
        key="GenomOncology|COMPANY",
        label="COMPANY",
        attrs={},
    )
    assert entity.terms == ("GenomOncology", "GO")

    node = Node.create(entity.dict())
    assert isinstance(node, Entity)


def test_custom_entity_class(apple):
    assert apple.label == "COMPANY"
