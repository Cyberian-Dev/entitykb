from pytest import fixture

from entitykb.graph.edges import EdgeIndex
from entitykb.models import Direction, Edge, Node

v0 = "VERB0"
v1 = "VERB1"


@fixture
def index(root):
    return EdgeIndex(root)


@fixture
def a():
    return Node(key="a")


@fixture
def b():
    return Node(key="b")


@fixture
def c():
    return Node(key="c")


def results(index, **kw):
    return list(index.iterate(**kw))


def count(index, **kw):
    data = results(index, **kw)
    return len(data)


def test_remove_start(a, b, c, index):
    def checks():
        return dict(
            t_v0=count(index, verbs=v0),
            t_v1=count(index, verbs=v1),
            t_a=count(index, nodes=a),
            t_b=count(index, nodes=b),
            t_c=count(index, nodes=c),
            o_c=count(index, nodes=c, directions=Direction.outgoing),
            i_c=count(index, nodes=c, directions=Direction.incoming),
        )

    assert checks() == dict(t_v0=0, t_v1=0, t_a=0, t_b=0, t_c=0, o_c=0, i_c=0)
    assert set() == index.get_verbs()

    data = {"say": "hello!"}
    e0 = Edge(start=b, verb=v0, end=a, data=data)
    index.save(e0)

    assert e0 in index
    assert index[e0.key] == e0

    index.reindex()
    assert checks() == dict(t_v0=2, t_v1=0, t_a=1, t_b=1, t_c=0, o_c=0, i_c=0)
    assert {v0} == index.get_verbs()

    e1 = Edge(start=c, verb=v1, end=a)
    index.save(e1)
    index.reindex()
    assert checks() == dict(t_v0=2, t_v1=2, t_a=2, t_b=1, t_c=1, o_c=1, i_c=0)
    assert {v0, v1} == index.get_verbs()

    e2 = Edge(start=b, verb=v0, end=c)
    index.save(e2)
    index.reindex()
    assert checks() == dict(t_v0=4, t_v1=2, t_a=2, t_b=2, t_c=2, o_c=1, i_c=1)
    assert {v0, v1} == index.get_verbs()

    # not new, but accepts existing edge
    index.save(e2)
    index.reindex()
    assert checks() == dict(t_v0=4, t_v1=2, t_a=2, t_b=2, t_c=2, o_c=1, i_c=1)
    assert {v0, v1} == index.get_verbs()

    # removes edge twice
    index.remove(e2)
    index.reindex()
    assert checks() == dict(t_v0=2, t_v1=2, t_a=2, t_b=1, t_c=1, o_c=1, i_c=0)
    assert {v0, v1} == index.get_verbs()

    index.remove(e1)
    index.reindex()
    assert checks() == dict(t_v0=2, t_v1=0, t_a=1, t_b=1, t_c=0, o_c=0, i_c=0)
    assert {v0} == index.get_verbs()

    index.remove(e0)
    index.reindex()
    assert checks() == dict(t_v0=0, t_v1=0, t_a=0, t_b=0, t_c=0, o_c=0, i_c=0)
    assert set() == index.get_verbs()
