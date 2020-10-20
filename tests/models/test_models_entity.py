from entitykb.models.entity import Entity


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
