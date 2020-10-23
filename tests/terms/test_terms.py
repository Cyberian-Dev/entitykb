import pytest

from entitykb.terms import TermsIndex
from entitykb.pipeline import Normalizer


@pytest.fixture()
def terms():
    normalizer = Normalizer.create()
    terms = TermsIndex(normalizer=normalizer)
    return terms


def test_length_clear_info(terms):
    assert 0 == len(terms)
    assert terms.info() == {
        "links_count": 0,
        "longest_word": 0,
        "nodes_count": 0,
        "sizeof_node": 32,
        "total_size": 0,
        "words_count": 0,
    }

    terms.add_term("key", "Hello")
    assert 1 == len(terms)
    assert terms.info() == {
        "links_count": 5,
        "longest_word": 5,
        "nodes_count": 6,
        "sizeof_node": 32,
        "total_size": 232,
        "words_count": 1,
    }

    terms.clear_data()
    assert 0 == len(terms)
    assert terms.info() == {
        "links_count": 0,
        "longest_word": 0,
        "nodes_count": 0,
        "sizeof_node": 32,
        "total_size": 0,
        "words_count": 0,
    }


def test_is_prefix(terms):
    terms.add_term("key", "Hello")

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

    # positive cases
    assert {a_key} == set(terms.iterate_term_keys("aa"))
    assert {b_key} == set(terms.iterate_term_keys("ab"))

    # negative cases
    assert set() == set(terms.iterate_term_keys("a"))
    assert set() == set(terms.iterate_term_keys("abc"))
