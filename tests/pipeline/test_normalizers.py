from string import punctuation


from entitykb.pipeline import LatinLowercaseNormalizer


def test_latin_lowercase_normalizer():
    normalizer = LatinLowercaseNormalizer()
    assert isinstance(normalizer.trie_characters, str)
    assert (26 + 10 + len(punctuation) + 1) == len(normalizer.trie_characters)

    original = "Mix of UPPER, lower, and ñôn-àscïî chars."
    normalized = normalizer(original)
    assert normalized == "mix of upper, lower, and non-ascii chars."
    assert len(original) == len(normalized)
