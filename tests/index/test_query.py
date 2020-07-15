from entitykb import Tag
from entitykb.index import QB, Query


def test_create_query():
    # complete example
    query = (
        QB()
        .walk(Tag.IS_A, Tag.HAS_A)
        .filter(label={"FOOD"})
        .exclude(label={"SAUCE"})
        .filter(is_a="Dessert|FOOD")
        .all()
    )

    # to dict
    data = query.dict()
    assert data == {
        "start": {},
        "steps": [
            {
                "incoming": True,
                "max_hops": None,
                "passthru": False,
                "tags": ["HAS_A", "IS_A"],
            },
            {"filters": [{"label": {"FOOD"}}]},
            {"exclude": True, "filters": [{"label": {"SAUCE"}}]},
            {
                "filters": [
                    {
                        "entities": ["Dessert|FOOD"],
                        "incoming": True,
                        "tags": ["IS_A"],
                    }
                ]
            },
        ],
        "goal": {},
    }

    # test round-tripping
    updated = Query.from_dict(data)
    assert updated.dict() == data
