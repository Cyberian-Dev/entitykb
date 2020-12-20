from string import punctuation

from entitykb.pipeline import LatinLowercaseNormalizer


def test_latin_lowercase_normalizer():
    normalizer = LatinLowercaseNormalizer()
    assert isinstance(normalizer.trie_characters, str)
    assert (26 + 10 + len(punctuation) + 1) == len(normalizer.trie_characters)

    # it converts 'extended' latin characters to ascii-lowercase
    original = "Mix of UPPER, lower, and ñôn-àscïî chars."
    normalized = normalizer(original)
    assert normalized == "mix of upper, lower, and non-ascii chars."
    assert len(original) == len(normalized)

    # it leaves non-english characters alone
    original = "喂 means 'hey'"
    normalized = normalizer(original)
    assert normalized == original
