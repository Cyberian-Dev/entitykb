import pytest

from entitykb.index import DefaultIndex
from entitykb.pipeline import DefaultNormalizer, DefaultTokenizer


@pytest.fixture
def index():
    index = DefaultIndex(
        tokenizer=DefaultTokenizer(), normalizer=DefaultNormalizer()
    )
    return index
