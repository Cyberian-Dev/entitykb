from pytest import fixture

from entitykb.graph.edge_index import EdgeIndex
from entitykb.models import Node, Edge

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
    e0 = Edge(start=b, verb=v, end=a)
    assert index.save(e0)

    assert 1 == count(index, nodes=a)
    assert 1 == count(index, nodes=b)
    assert 0 == count(index, nodes=c)
    assert 2 == count(index, verbs=v)
    assert 1 == count(index, verbs=v, nodes=a)

    e1 = Edge(start=c, verb=v, end=a)
    assert index.save(e1)

    assert 2 == count(index, nodes=a)
    assert 1 == count(index, nodes=b)
    assert 1 == count(index, nodes=c)
    assert 4 == count(index, verbs=v)
    assert 2 == count(index, verbs=v, nodes=a)

    # not new
    assert not index.save(e0)

    assert 2 == count(index, nodes=a)
    assert 1 == count(index, nodes=b)
    assert 1 == count(index, nodes=c)
    assert 4 == count(index, verbs=v)
    assert 2 == count(index, verbs=v, nodes=a)

    index.remove(e1)

    assert 1 == count(index, nodes=a)
    assert 1 == count(index, nodes=b)
    assert 0 == count(index, nodes=c)
    assert 2 == count(index, verbs=v)
    assert 1 == count(index, verbs=v, nodes=a)

    index.remove(e1)

    assert 1 == count(index, nodes=a)
    assert 1 == count(index, nodes=b)
    assert 0 == count(index, nodes=c)
    assert 2 == count(index, verbs=v)
    assert 1 == count(index, verbs=v, nodes=a)

    index.remove(e0)

    assert 0 == count(index, nodes=a)
    assert 0 == count(index, nodes=b)
    assert 0 == count(index, nodes=c)
    assert 0 == count(index, verbs=v)
    assert 0 == count(index, verbs=v, nodes=a)
