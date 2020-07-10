from entitykb.normalizers import DefaultNormalizer
from entitykb.index.terms import DefaultTerms


def test_add_get_terms():
    terms = DefaultTerms(normalizer=DefaultNormalizer())
    terms.add_terms(1.0, "ENTITY", ("Apple", "Apple, Inc."))
    terms.add_terms(2.0, "ENTITY", ("apple",))

    print(terms.get("apple"))

    assert [1.0, 2.0] == sorted(terms.get("apple"))
    assert [1.0, 2.0] == sorted(terms.get("Apple"))
    assert [1.0, 2.0] == sorted(terms.get("APPLE"))


def test_reset():
    terms = DefaultTerms(normalizer=DefaultNormalizer())
    terms.reset_data()

    assert 0 == len(terms.trie)
    assert 0 == len(terms)
    assert 0 == terms.info().get("nodes_count")
