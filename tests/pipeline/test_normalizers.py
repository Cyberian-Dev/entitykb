from string import punctuation


from entitykb.pipeline import Normalizer, LatinLowercaseNormalizer


def test_construct():
    normalizer = Normalizer.create()
    assert isinstance(normalizer, LatinLowercaseNormalizer)

    normalizer = Normalizer.create(LatinLowercaseNormalizer)
    assert isinstance(normalizer, LatinLowercaseNormalizer)

    class_name = "entitykb.pipeline.LatinLowercaseNormalizer"
    normalizer = LatinLowercaseNormalizer.create(class_name)
    assert isinstance(normalizer, LatinLowercaseNormalizer)

    argument = LatinLowercaseNormalizer()
    normalizer = Normalizer.create(argument)
    assert argument is normalizer


def test_default_normalizer():
    normalizer = Normalizer.create()
    assert isinstance(normalizer.trie_characters, str)
    assert (26 + 10 + len(punctuation) + 1) == len(normalizer.trie_characters)

    original = "Mix of UPPER, lower, and ñôn-àscïî chars."
    normalized = normalizer(original)
    assert normalized == "mix of upper, lower, and non-ascii chars."
    assert len(original) == len(normalized)
