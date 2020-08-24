import pytest
import tempfile
import entitykb
from entitykb.interface import schema, KB


@pytest.fixture()
def root_dir():
    return tempfile.mkdtemp()


@pytest.fixture()
def core(root_dir):
    return entitykb.KB.create(root_dir=root_dir)


@pytest.fixture()
def kb(core):
    return KB(core=core)


def test_parse(kb: KB):
    doc = kb.parse("This is a doc")
    assert isinstance(doc, entitykb.model.Doc)
    assert 4 == len(doc.tokens)
