from entitykb.models.query import (
    Query,
    WalkStep,
    FilterStep,
    Direction,
    Comparison,
    QB,
    A,
    AttrCriteria,
)


def test_empty_qb():
    q = QB().all()
    assert isinstance(q, Query)
    assert 0 == len(q)


def test_walk_nodes():
    q = QB().all_nodes("IS_A").all()
    assert q[0] == WalkStep(
        tags=["IS_A"],
        max_hops=1,
        directions=(Direction.outgoing, Direction.incoming),
    )

    q = QB().out_nodes("IS_A").all()
    assert q[0] == WalkStep(
        tags=["IS_A"], max_hops=1, directions=Direction.outgoing
    )

    q = QB().in_nodes("IS_A").all()
    assert q[0] == WalkStep(
        tags=["IS_A"], max_hops=1, directions=Direction.incoming
    )


def test_filter_nodes():
    q = QB().include(A.label == "PERSON").all()
    assert q[0] == FilterStep(
        criteria=(
            AttrCriteria(
                attr_name="label", compare=Comparison.eq, value="PERSON"
            )
        )
    )

    q = QB().exclude(A.label == "PERSON").all()
    assert q[0] == FilterStep(
        criteria=(
            AttrCriteria(
                attr_name="label", compare=Comparison.eq, value="PERSON"
            )
        ),
        exclude=True,
    )
