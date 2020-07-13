from entitykb import Tag
from entitykb.index.query import QB, Query


def test_create_query():
    # complete example
    query = QB().walk(Tag.IS_A, Tag.HAS_A).filter().exclude().all()

    # to dict
    data = query.dict()
    assert data == {
        "start": {"entities": []},
        "steps": [
            {
                "tags": ["HAS_A", "IS_A"],
                "incoming": True,
                "max_hops": None,
                "passthru": False,
            },
            {"include": True},
            {"include": False},
        ],
        "goal": {"limit": None},
    }

    # test round-tripping
    updated = Query.from_dict(data)
    assert updated.dict() == data
