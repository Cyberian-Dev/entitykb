from pytest import fixture

from entitykb.graph.edge_index import EdgeIndex
from entitykb.models import Node, Edge, Direction

v = "VERB"


@fixture
def index():
    return EdgeIndex()


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
            t_v=count(index, verbs=v),
            t_a=count(index, nodes=a),
            t_b=count(index, nodes=b),
            t_c=count(index, nodes=c),
            o_c=count(index, nodes=c, directions=Direction.outgoing),
            i_c=count(index, nodes=c, directions=Direction.incoming),
        )

    assert checks() == dict(t_v=0, t_a=0, t_b=0, t_c=0, o_c=0, i_c=0)

    e0 = Edge(start=b, verb=v, end=a)
    index.save(e0)
    assert checks() == dict(t_v=2, t_a=1, t_b=1, t_c=0, o_c=0, i_c=0)

    e1 = Edge(start=c, verb=v, end=a)
    index.save(e1)
    assert checks() == dict(t_v=4, t_a=2, t_b=1, t_c=1, o_c=1, i_c=0)

    e2 = Edge(start=b, verb=v, end=c)
    index.save(e2)
    assert checks() == dict(t_v=6, t_a=2, t_b=2, t_c=2, o_c=1, i_c=1)

    # not new, but accepts existing edge
    index.save(e2)
    assert checks() == dict(t_v=8, t_a=2, t_b=3, t_c=3, o_c=1, i_c=2)

    # removes edge twice
    index.remove(e2)
    assert checks() == dict(t_v=4, t_a=2, t_b=1, t_c=1, o_c=1, i_c=0)

    index.remove(e1)
    assert checks() == dict(t_v=2, t_a=1, t_b=1, t_c=0, o_c=0, i_c=0)

    index.remove(e0)
    assert checks() == dict(t_v=0, t_a=0, t_b=0, t_c=0, o_c=0, i_c=0)
