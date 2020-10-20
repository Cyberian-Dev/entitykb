import os

from entitykb import KB, Doc, Edge


def test_parse(kb: KB):
    doc = kb.parse("This is a doc")
    assert isinstance(doc, Doc)
    assert 4 == len(doc.tokens)


def test_creates_files(root, kb: KB, apple):
    assert os.path.isfile(os.path.join(root, "config.json"))
    assert not os.path.isfile(os.path.join(root, "index.db"))

    kb.save_node(apple)
    assert not os.path.isfile(os.path.join(root, "index.db"))

    kb.commit()
    assert os.path.isfile(os.path.join(root, "index.db"))


def test_save_entity(kb: KB, apple):
    kb.save_node(apple)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple


def test_save_load_sync(root, kb: KB, apple):
    kb.save_node(apple)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple

    kb.commit()

    kb = KB(root=root)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple

    kb = KB(root=root)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple


def test_save_edge(kb: KB, apple):
    assert 1 == kb.save_node(apple)
    assert 1 == len(kb)
    assert apple == kb.get_node(apple.key)

    edge = Edge(start=apple, end=apple, tag="IS_A")
    kb.save_edge(edge)

    assert kb.info().keys() == {"graph", "storage", "terms", "config"}

    kb.reset()
    assert 0 == len(kb)
