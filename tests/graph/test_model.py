from entitykb.graph import (
    Node,
    Entity,
    Edge,
    Query,
    WalkStep,
    FilterStep,
    Filter,
)


def test_node():
    empty = Node()
    assert 36 == len(empty.key)
    assert empty.dict() == dict(
        key=empty.key, label=None, meta={}, _klass="entitykb.graph.model.Node"
    )

    node = Node(key="ENTITY|LABEL", label="LABEL")
    assert node.dict() == dict(
        key="ENTITY|LABEL",
        label="LABEL",
        meta={},
        _klass="entitykb.graph.model.Node",
    )

    # warning: don't use eval in production code, just an example.
    assert node == eval(repr(node))


def test_entity():
    empty = Entity(name="empty")
    assert empty.dict() == dict(
        name="empty",
        synonyms=tuple(),
        key="empty|ENTITY",
        label="ENTITY",
        meta={},
        _klass="entitykb.graph.model.Entity",
    )
    assert empty.terms == ("empty",)

    entity = Entity(name="GenomOncology", label="COMPANY", synonyms=("GO",))
    assert entity.dict() == dict(
        name="GenomOncology",
        synonyms=("GO",),
        key="GenomOncology|COMPANY",
        label="COMPANY",
        meta={},
        _klass="entitykb.graph.model.Entity",
    )
    assert entity.terms == ("GenomOncology", "GO")

    # warning: don't use eval in production code, just an example.
    assert entity == eval(repr(entity))


def test_edge():
    start = Node()
    end = Node()
    edge = Edge(start=start, end=end, tag="IS_A")
    assert edge.dict() == dict(
        start=start.key,
        tag="IS_A",
        end=end.key,
        weight=1,
        meta={},
        _klass="entitykb.graph.model.Edge",
    )

    # warning: don't use eval in production code, just an example.
    assert edge == eval(repr(edge))

    two = start >> "IS_A" >> end
    assert two == edge
    assert two.dict() == edge.dict()


def test_create_query_single_node():
    n = Node()
    q = Query((n.key,), steps=())
    assert q.starts == (n.key,)
    assert q.steps == []
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "_klass": "entitykb.graph.model.Query",
        "starts": (n.key,),
        "limit": None,
        "offset": 0,
        "steps": (),
    }


def test_create_walk_step_only():
    walk_step = WalkStep()
    q = Query(starts=(), steps=walk_step)
    assert q.starts == ()
    assert q.steps == [walk_step]
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "_klass": "entitykb.graph.model.Query",
        "starts": (),
        "limit": None,
        "offset": 0,
        "steps": (
            {
                "_klass": "entitykb.graph.model.WalkStep",
                "directions": ("incoming",),
                "max_hops": None,
                "passthru": False,
                "tags": (),
            },
        ),
    }

    q2 = Query.create(q.dict())
    assert q2.dict() == q.dict()


def test_create_filter_step_only():
    filter = Filter()
    filter_step = FilterStep(filters=filter)
    q = Query(starts=(), steps=filter_step)
    assert q.steps == [filter_step]
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "_klass": "entitykb.graph.model.Query",
        "starts": (),
        "limit": None,
        "offset": 0,
        "steps": (
            {
                "_klass": "entitykb.graph.model.FilterStep",
                "exclude": False,
                "filters": (
                    {
                        "_klass": "entitykb.graph.model.Filter",
                        "directions": ("outgoing", "incoming"),
                        "keys": (),
                        "labels": (),
                        "self_ok": False,
                        "tags": (),
                    },
                ),
                "join_type": "AND",
            },
        ),
    }

    q2 = Query.create(q.dict())
    assert q2.dict() == q.dict()
