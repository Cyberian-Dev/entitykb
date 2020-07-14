from entitykb import Tag
from entitykb.index import QB, Query


def test_create_query():
    # complete example
    query = (
        QB()
        .walk(Tag.IS_A, Tag.HAS_A)
        .filter(labels={"FOOD"})
        .exclude(labels={"SAUCE"})
        .all()
    )

    # to dict
    data = query.dict()
    assert data == {
        "goal": {"limit": None},
        "start": {"entities": []},
        "steps": [
            {
                "incoming": True,
                "max_hops": None,
                "passthru": False,
                "tags": ["HAS_A", "IS_A"],
            },
            {
                "exclude": False,
                "filters": [{"labels": {"FOOD"}}],
                "join_type": "AND",
            },
            {
                "exclude": True,
                "filters": [{"labels": {"SAUCE"}}],
                "join_type": "AND",
            },
        ],
    }

    # test round-tripping
    updated = Query.from_dict(data)
    assert updated.dict() == data
