from entitykb.graph.nodes import NodeIndex
from entitykb.models import Entity, Node


def test_node_cache(root, normalizer):
    node = Node()
    index = NodeIndex(root, normalizer)

    index.save(node)
    assert node == index.get(node.key)
    assert node in index
    assert node.key in index
    assert 1 == len(index)

    index.remove(node)
    assert index.get(node.key) is None
    assert node not in index
    assert node.key not in index
    assert 0 == len(index)


def test_node_index(root, normalizer):
    index = NodeIndex(root, normalizer)
    aa = Entity(name="aa", label="A")
    bb = Entity(name="bb", label="B")
    index.save(aa)
    index.save(bb)

    def get(**kwargs):
        return list(index.iterate(**kwargs))

    # after saves, before reindex
    assert set() == index.get_labels()
    assert not get(prefixes="a")

    # reindex saves
    index.reindex()
    assert {"A", "B"} == index.get_labels()
    assert get(prefixes="a")
    assert not get(terms="a")
    assert get(terms="aa")
    assert get(terms="aa", labels=["A"])
    assert get(terms="aa", labels=["A"], keys=aa.key)

    index.remove(aa.key)

    # after removal, before reindex
    assert get(prefixes="a")

    # reindex removal
    index.reindex()
    assert {"B"} == index.get_labels()
    assert not get(prefixes="a")
    assert get(prefixes="b")
    assert get(terms="bb")
    assert get(terms="bb", labels="B")
