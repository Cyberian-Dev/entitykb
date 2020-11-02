import pytest
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


def test_save_for_entity_and_edge(kb: KB, apple):
    assert apple == kb.save(apple)
    assert 1 == len(kb)
    assert apple == kb.get_node(apple.key)

    edge = Edge(start=apple, verb="IS_A", end=apple)
    kb.save(edge)

    assert kb.info()["graph"] == {
        "nodes": 1,
        "edges": 1,
    }

    kb.remove_node(apple.key)
    assert kb.info()["graph"] == {
        "nodes": 0,
        "edges": 0,
    }


def test_kb_save_bool_clear(kb: KB, apple):
    assert bool(kb)

    assert apple == kb.save(apple)
    assert 1 == len(kb)
    kb.clear()

    assert 0 == len(kb)
    assert bool(kb)


def test_kb_save_invalid(kb: KB):
    with pytest.raises(RuntimeError):
        kb.save("invalid!")


def test_get_schema(kb: KB):
    schema = kb.get_schema()
    assert schema.keys() == {"nodes", "edges"}
    assert {"NODE", "ENTITY"}.issubset(schema["nodes"].keys())
    assert {"EDGE"}.issubset(schema["edges"].keys())
