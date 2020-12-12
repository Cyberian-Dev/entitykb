from entitykb.contrib.date import DateResolver
from entitykb.pipeline import TermResolver


def test_date_resolver_is_prefix():
    resolver = DateResolver()

    assert resolver.is_prefix("2019")
    assert resolver.is_prefix("2019-")
    assert resolver.is_prefix("2019-01")
    assert resolver.is_prefix("2019-01-01")
    assert resolver.is_prefix("October")
    assert resolver.is_prefix("October 1")
    assert resolver.is_prefix("October 1, ")

    assert not resolver.is_prefix("Nonsense!")
    assert not resolver.is_prefix("2017 07 19 J")


def test_date_resolver_find_valid():
    resolver = DateResolver()
    assert "2019-01-01" == resolver.resolve("2019-01-01")[0].name
    assert "2019-01-01" == resolver.resolve("Jan 1st, 2019")[0].name
    assert "2019-01-01" == resolver.resolve("01/01/19")[0].name
    assert "2019-01-01" == resolver.resolve("2019-JAN-01")[0].name


def test_date_resolver_fail_invalid():
    resolver = DateResolver()
    result = resolver.resolve("Nonsense!")
    assert not result

    result = resolver.resolve("2017 07 19 J")
    assert not result

    result = resolver.resolve("3")
    assert not result

    result = resolver.resolve("15t")
    assert not result


def test_default_resolver(kb, apple):
    resolver = TermResolver(kb=kb)
    kb.save_node(apple)
    kb.reindex()

    assert resolver.is_prefix("a")
    assert resolver.is_prefix("apple")
    assert not resolver.is_prefix("b")
    assert not resolver.is_prefix("apple, ink.")

    assert [apple] == resolver.resolve("apple")
    assert [apple] == resolver.resolve("apple, inc.")

    assert not resolver.resolve("banana")
    assert not resolver.resolve("apple, ink.")
    assert not resolver.is_prefix("apple, ink")
