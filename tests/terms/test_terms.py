import pytest

from entitykb.terms import Terms
from entitykb.pipeline import Normalizer
from entitykb.graph import Node


@pytest.fixture()
def terms():
    normalizer = Normalizer.create()
    terms = Terms(normalizer=normalizer)
    return terms


def test_is_prefix(terms):
    terms.add_term("Hello", Node())

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
    a = Node()
    b = Node()
    terms.add_term("aa", a)
    terms.add_term("ab", b)

    # positive cases
    assert {a.key, b.key} == set(terms.iterate_prefix_keys("a"))
    assert {b.key} == set(terms.iterate_prefix_keys("ab"))

    # negative cases
    assert set() == set(terms.iterate_prefix_keys("abc"))
    assert set() == set(terms.iterate_prefix_keys("b"))


def test_iterate_term(terms):
    a = Node()
    b = Node()
    terms.add_term("aa", a)
    terms.add_term("ab", b)

    # positive cases
    assert {a.key} == set(terms.iterate_term_keys("aa"))
    assert {b.key} == set(terms.iterate_term_keys("ab"))

    # negative cases
    assert set() == set(terms.iterate_term_keys("a"))
    assert set() == set(terms.iterate_term_keys("abc"))
