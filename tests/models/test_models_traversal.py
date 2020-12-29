from entitykb.models import (
    Comparison,
    Criteria,
    Direction,
    EdgeCriteria,
    F,
    FieldCriteria,
    FilterStep,
    T,
    V,
    WalkStep,
)


def test_verb():
    assert V.IS_A == V.IS_A
    assert id(V.IS_A) == id(V.IS_A)
    assert V["IS_A"] == V["is_a"]


def test_create_walk_step_defaults():
    walk_step = WalkStep()
    assert walk_step.dict() == {
        "directions": [Direction.incoming],
        "max_hops": 1,
        "passthru": False,
        "verbs": [],
    }


def test_create_filter_step_only():
    filter_step = FilterStep(criteria=F.number >= 3)
    assert filter_step.dict() == {
        "all": False,
        "criteria": [
            {"field": "number", "compare": "gte", "type": "field", "value": 3}
        ],
        "exclude": False,
    }


def test_simple_attr_criteria():
    a = F.label.exact("FOOD")
    assert a.dict() == {
        "field": "label",
        "compare": "exact",
        "value": "FOOD",
        "type": "field",
    }

    a2 = Criteria.create(**a.dict())
    assert a.dict() == a2.dict()


def test_rel_criteria():
    r = V.is_a >> "Fruit|FOOD"
    assert r.dict() == {
        "verbs": ["IS_A"],
        "directions": [Direction.outgoing],
        "keys": ["Fruit|FOOD"],
        "type": "edge",
    }

    r2 = Criteria.create(r.dict())
    assert r.dict() == r2.dict()


def test_empty_traversal():
    t = T()
    assert isinstance(t, T)
    assert 0 == len(t)
    assert t.dict() == []


def test_copy():
    t1 = T().all_nodes("IS_A")
    t2 = t1.copy()
    assert 1 == len(t2)

    t2.include(F.label == "A")
    assert 2 == len(t2)
    assert 1 == len(t1)


def test_walk_nodes():
    t = T().all_nodes("IS_A")
    assert t[0] == WalkStep(
        verbs=["IS_A"],
        max_hops=1,
        directions=[Direction.outgoing, Direction.incoming],
    )
    assert t.dict() == [
        {
            "directions": [Direction.outgoing, Direction.incoming],
            "max_hops": 1,
            "passthru": False,
            "verbs": ["IS_A"],
        }
    ]

    t = T().out_nodes("IS_A")
    assert t[0] == WalkStep(
        verbs=["IS_A"], max_hops=1, directions=[Direction.outgoing]
    )

    t = T().in_nodes("IS_A")
    assert t[0] == WalkStep(
        verbs=["IS_A"], max_hops=1, directions=[Direction.incoming]
    )


def test_filter_by_field():
    t = T().include(F.label == "PERSON")
    assert t[0] == FilterStep(
        criteria=[
            FieldCriteria(
                field="label", compare=Comparison.exact, value="PERSON"
            )
        ]
    )

    t = T().exclude(F.label == "PERSON")
    assert t[0] == FilterStep(
        criteria=[
            FieldCriteria(
                field="label", compare=Comparison.exact, value="PERSON"
            )
        ],
        exclude=True,
    )


def test_filter_by_edge():
    t = T().include(V.is_a >> "Apple|COMPANY")
    assert t[0] == FilterStep(
        criteria=[
            EdgeCriteria(
                verbs=["IS_A"],
                directions=[Direction.outgoing],
                keys=["Apple|COMPANY"],
            )
        ]
    )
