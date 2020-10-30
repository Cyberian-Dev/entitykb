from entitykb.models import (
    F,
    Criteria,
    Direction,
    FilterStep,
    Query,
    WalkStep,
    Tag,
)


def test_create_query_single_node():
    q = Query(steps=())
    assert q.steps == []
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "limit": None,
        "offset": 0,
        "steps": [],
    }


def test_create_walk_step_only():
    walk_step = WalkStep()
    q = Query(steps=walk_step)
    assert q.steps == [walk_step]
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "limit": None,
        "offset": 0,
        "steps": [
            {
                "directions": [Direction.incoming],
                "max_hops": 1,
                "passthru": False,
                "tags": [],
            },
        ],
    }

    q2 = Query(**q.dict())
    assert q2.dict() == q.dict()


def test_create_filter_step_only():
    filter_step = FilterStep(criteria=F.number >= 3)
    q = Query(steps=filter_step)
    assert q.steps == [filter_step]
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "limit": None,
        "offset": 0,
        "steps": [
            {
                "all": False,
                "criteria": [
                    {
                        "attr_name": "number",
                        "compare": ">=",
                        "type": "field",
                        "value": 3,
                    }
                ],
                "exclude": False,
            }
        ],
    }

    q2 = Query(**q.dict())
    assert q2.dict() == q.dict()


def test_simple_attr_criteria():
    a = F.label == "FOOD"
    assert a.dict() == {
        "attr_name": "label",
        "compare": "==",
        "value": "FOOD",
        "type": "field",
    }

    a2 = Criteria.create(**a.dict())
    assert a.dict() == a2.dict()


def test_rel_criteria():
    r = Tag.is_a >> "Fruit|FOOD"
    assert r.dict() == {
        "tags": ["IS_A"],
        "directions": [Direction.outgoing],
        "nodes": ["Fruit|FOOD"],
        "type": "edge",
    }

    r2 = Criteria.create(r.dict())
    assert r.dict() == r2.dict()
