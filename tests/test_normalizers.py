from entitykb.normalizers import Normalizer, DefaultNormalizer


def test_construct():
    normalizer = Normalizer.create()
    assert isinstance(normalizer, DefaultNormalizer)

    normalizer = Normalizer.create(DefaultNormalizer)
    assert isinstance(normalizer, DefaultNormalizer)

    class_name = "entitykb.normalizers.DefaultNormalizer"
    normalizer = DefaultNormalizer.create(class_name)
    assert isinstance(normalizer, DefaultNormalizer)

    argument = DefaultNormalizer()
    normalizer = Normalizer.create(argument)
    assert argument is normalizer


def test_default_normalizer():
    normalizer = Normalizer.create()
    original = "Mix of UPPER, lower, and ñôn-àscïî chars."
    normalized = normalizer(original)
    assert normalized == "mix of upper, lower, and non-ascii chars."
    assert len(original) == len(normalized)
