import pytest

from entitykb import (
    DefaultNormalizer,
    DefaultTokenizer,
)
from entitykb.index import DefaultIndex


@pytest.fixture
def index():
    index = DefaultIndex(
        tokenizer=DefaultTokenizer(), normalizer=DefaultNormalizer()
    )
    return index
