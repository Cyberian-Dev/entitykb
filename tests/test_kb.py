import pytest
import os
import tempfile

import entitykb


@pytest.fixture()
def root_dir():
    return tempfile.mkdtemp()


@pytest.fixture()
def kb(root_dir):
    return entitykb.KB.create(root_dir=root_dir)


def test_creates_files(root_dir, kb: entitykb.KB, apple):
    assert os.path.isfile(os.path.join(root_dir, "config.json"))
    assert not os.path.isfile(os.path.join(root_dir, "index.db"))

    kb.add(apple)
    assert not os.path.isfile(os.path.join(root_dir, "index.db"))

    kb.commit()
    assert os.path.isfile(os.path.join(root_dir, "index.db"))


def test_add_entity(kb: entitykb.KB, apple):
    kb.add(apple)
    assert (kb("AAPL")).entities[0].entity == apple
    assert (kb("Apple, Inc.")).entities[0].entity == apple
    assert (kb("Apple,Inc.")).entities[0].entity == apple


def test_save_load_sync(root_dir, kb: entitykb.KB, apple):
    kb.add(apple)
    kb.commit()

    kb = entitykb.KB.create(root_dir=root_dir)
    assert (kb("AAPL")).entities[0].entity == apple
    assert (kb("Apple, Inc.")).entities[0].entity == apple
    assert (kb("Apple,Inc.")).entities[0].entity == apple

    kb = entitykb.KB.create(root_dir=root_dir)
    assert (kb("AAPL")).entities[0].entity == apple
    assert (kb("Apple, Inc.")).entities[0].entity == apple
    assert (kb("Apple,Inc.")).entities[0].entity == apple
