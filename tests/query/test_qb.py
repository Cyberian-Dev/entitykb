from entitykb.models.query import (
    Query,
    WalkStep,
    FilterStep,
    Direction,
    Comparison,
    QB,
    F,
    FieldCriteria,
)


def test_empty_qb():
    q = QB().all()
    assert isinstance(q, Query)
    assert 0 == len(q)


def test_walk_nodes():
    q = QB().all_nodes("IS_A").all()
    assert q[0] == WalkStep(
        verbs=["IS_A"],
        max_hops=1,
        directions=(Direction.outgoing, Direction.incoming),
    )

    q = QB().out_nodes("IS_A").all()
    assert q[0] == WalkStep(
        verbs=["IS_A"], max_hops=1, directions=Direction.outgoing
    )

    q = QB().in_nodes("IS_A").all()
    assert q[0] == WalkStep(
        verbs=["IS_A"], max_hops=1, directions=Direction.incoming
    )


def test_filter_nodes():
    q = QB().include(F.label == "PERSON").all()
    assert q[0] == FilterStep(
        criteria=(
            FieldCriteria(
                attr_name="label", compare=Comparison.exact, value="PERSON"
            )
        )
    )

    q = QB().exclude(F.label == "PERSON").all()
    assert q[0] == FilterStep(
        criteria=(
            FieldCriteria(
                attr_name="label", compare=Comparison.exact, value="PERSON"
            )
        ),
        exclude=True,
    )
