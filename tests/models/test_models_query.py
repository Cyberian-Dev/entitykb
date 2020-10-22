from entitykb.models import (
    AttrCriteria,
    Criteria,
    Direction,
    FilterStep,
    Node,
    Query,
    RelCriteria,
    WalkStep,
)


def test_create_query_single_node():
    q = Query(steps=())
    assert q.steps == []
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "limit": None,
        "offset": 0,
        "steps": (),
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
        "steps": (
            {
                "directions": ("incoming",),
                "max_hops": 1,
                "passthru": False,
                "tags": (),
            },
        ),
    }

    q2 = Query.create(q.dict())
    assert q2.dict() == q.dict()


def test_create_filter_step_only():
    filter_step = FilterStep()
    q = Query(steps=filter_step)
    assert q.steps == [filter_step]
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "limit": None,
        "offset": 0,
        "steps": ({"criteria": (None,), "exclude": False, "all": False},),
    }

    q2 = Query.create(q.dict())
    assert q2.dict() == q.dict()


def test_simple_attr_criteria():
    a = AttrCriteria.label == "FOOD"
    assert a.dict() == {
        "attr_name": "label",
        "compare": "==",
        "value": "FOOD",
    }

    a2 = Criteria.create(**a.dict())
    assert a.dict() == a2.dict()


def test_simple_rel_criteria():
    n = Node()
    r = RelCriteria.is_a >> n
    compare = RelCriteria(tags="IS_A", directions=Direction.outgoing, nodes=n)
    assert r.dict() == compare.dict()

    r2 = Criteria.create(**r.dict())
    assert r.dict() == r2.dict()
