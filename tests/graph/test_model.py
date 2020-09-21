from entitykb.graph import (
    AttrCriteria,
    Direction,
    Edge,
    Entity,
    FilterStep,
    Node,
    Query,
    RelCriteria,
    WalkStep,
)


def test_node():
    empty = Node()
    assert 36 == len(empty.key)
    assert empty.dict() == dict(
        key=empty.key, label=None, attrs={}, _klass="entitykb.graph.model.Node"
    )

    node = Node(key="ENTITY|LABEL", label="LABEL")
    assert node.dict() == dict(
        key="ENTITY|LABEL",
        label="LABEL",
        attrs={},
        _klass="entitykb.graph.model.Node",
    )


def test_entity():
    empty = Entity(name="empty")
    assert empty.dict() == dict(
        name="empty",
        synonyms=tuple(),
        key="empty|ENTITY",
        label="ENTITY",
        attrs={},
        _klass="entitykb.graph.model.Entity",
    )
    assert empty.terms == ("empty",)

    entity = Entity(name="GenomOncology", label="COMPANY", synonyms=("GO",))
    assert entity.dict() == dict(
        name="GenomOncology",
        synonyms=("GO",),
        key="GenomOncology|COMPANY",
        label="COMPANY",
        attrs={},
        _klass="entitykb.graph.model.Entity",
    )
    assert entity.terms == ("GenomOncology", "GO")


def test_edge():
    start = Node()
    end = Node()
    edge = Edge(start=start, end=end, tag="IS_A")
    assert edge.dict() == dict(
        start=start.key,
        tag="IS_A",
        end=end.key,
        weight=1,
        attrs={},
        _klass="entitykb.graph.model.Edge",
    )

    two = start >> "IS_A" >> end
    assert two == edge
    assert two.dict() == edge.dict()

    three = end << "IS_A" << start
    assert three == edge
    assert three.dict() == edge.dict()


def test_create_query_single_node():
    q = Query(steps=())
    assert q.steps == []
    assert q.limit is None
    assert q.offset == 0
    assert q.dict() == {
        "_klass": "entitykb.graph.model.Query",
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
        "_klass": "entitykb.graph.model.Query",
        "limit": None,
        "offset": 0,
        "steps": (
            {
                "_klass": "entitykb.graph.model.WalkStep",
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
        "_klass": "entitykb.graph.model.Query",
        "limit": None,
        "offset": 0,
        "steps": (
            {
                "_klass": "entitykb.graph.model.FilterStep",
                "criteria": (None,),
                "exclude": False,
                "all": False,
            },
        ),
    }

    q2 = Query.create(q.dict())
    assert q2.dict() == q.dict()


def test_simple_attr_criteria():
    a = AttrCriteria.label == "FOOD"
    assert a.dict() == {
        "_klass": "entitykb.graph.model.AttrCriteria",
        "attr_name": "label",
        "compare": "==",
        "value": "FOOD",
    }


def test_simple_rel_criteria():
    n = Node()
    r = RelCriteria.is_a >> n
    compare = RelCriteria(tags="IS_A", directions=Direction.outgoing, nodes=n)
    assert r.dict() == compare.dict()
