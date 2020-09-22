import os

from entitykb import KB, Doc


def test_parse(kb: KB):
    doc = kb.parse("This is a doc")
    assert isinstance(doc, Doc)
    assert 4 == len(doc.tokens)


def test_creates_files(root_dir, kb: KB, apple):
    assert os.path.isfile(os.path.join(root_dir, "config.json"))
    assert not os.path.isfile(os.path.join(root_dir, "index.db"))

    kb.save_entity(apple)
    assert not os.path.isfile(os.path.join(root_dir, "index.db"))

    kb.commit()
    assert os.path.isfile(os.path.join(root_dir, "index.db"))


def test_save_entity(kb: KB, apple):
    kb.save_entity(apple)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple


def test_save_load_sync(root_dir, kb: KB, apple):
    kb.save_entity(apple)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple

    kb.commit()

    kb = KB(root_dir=root_dir)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple

    kb = KB(root_dir=root_dir)
    assert (kb.parse("AAPL")).entities[0].entity == apple
    assert (kb.parse("Apple, Inc.")).entities[0].entity == apple
    assert (kb.parse("Apple,Inc.")).entities[0].entity == apple
