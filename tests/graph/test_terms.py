import pytest

from entitykb.graph.terms import DawgTermsIndex
from entitykb.pipeline import Normalizer


@pytest.fixture()
def terms():
    normalizer = Normalizer.create()
    terms = DawgTermsIndex.create(normalizer=normalizer)
    return terms


def test_length_clear_info(terms):
    assert 0 == len(terms)
    assert terms.info() == {
        "count": 0,
    }

    terms.add_term("key", "Hello")
    terms.commit()
    assert 1 == len(terms)
    assert terms.info() == {
        "count": 1,
    }

    terms.clear_data()
    assert 0 == len(terms)
    assert terms.info() == {
        "count": 0,
    }


def test_is_prefix(terms):
    terms.add_term("key", "Hello")
    terms.commit()

    # positive cases
    assert terms.is_prefix("Hello")
    assert terms.is_prefix("hello")
    assert terms.is_prefix("he")
    assert terms.is_prefix("h")

    # negative cases
    assert not terms.is_prefix("h3")
    assert not terms.is_prefix("9")
    assert not terms.is_prefix("9")


def test_iterate_prefix(terms):
    a_key = "a"
    b_key = "b"
    terms.add_term(a_key, "aa")
    terms.add_term(b_key, "ab")
    terms.commit()

    # positive cases
    assert {a_key, b_key} == set(terms.iterate_prefix_keys("a"))
    assert {b_key} == set(terms.iterate_prefix_keys("ab"))

    # negative cases
    assert set() == set(terms.iterate_prefix_keys("abc"))
    assert set() == set(terms.iterate_prefix_keys("b"))


def test_iterate_term(terms):
    a_key = "a"
    b_key = "b"
    terms.add_term(a_key, "aa")
    terms.add_term(b_key, "ab")
    terms.add_term(b_key, "abc")
    terms.commit()

    # positive cases
    assert {a_key} == set(terms.iterate_term_keys("aa"))
    assert {b_key} == set(terms.iterate_term_keys("ab"))
    assert {b_key} == set(terms.iterate_term_keys("abc"))

    terms.remove_term(b_key, "abc")
    terms.commit()

    # negative cases
    assert set() == set(terms.iterate_term_keys("a"))
    assert set() == set(terms.iterate_term_keys("abc"))
