from entitykb.contrib.date import DateResolver, Date
from entitykb.pipeline import (
    TermResolver,
    Resolver,
    LatinLowercaseNormalizer,
    WhitespaceTokenizer,
)


def test_resolver_construct(kb):
    tokenizer = WhitespaceTokenizer()
    normalizer = LatinLowercaseNormalizer()

    assert isinstance(
        Resolver.create(
            None,
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            kb=kb,
        ),
        TermResolver,
    )

    assert isinstance(
        Resolver.create(
            TermResolver,
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            kb=kb,
        ),
        TermResolver,
    )

    assert isinstance(
        Resolver.create(
            DateResolver,
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            kb=kb,
        ),
        DateResolver,
    )

    assert isinstance(
        Resolver.create(
            "entitykb.contrib.date.DateResolver",
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            kb=kb,
        ),
        DateResolver,
    )


def test_date_resolver_is_prefix(kb):
    resolver = DateResolver(
        tokenizer=WhitespaceTokenizer(),
        normalizer=LatinLowercaseNormalizer(),
        kb=kb,
    )

    assert resolver.is_prefix("2019")
    assert resolver.is_prefix("2019-")
    assert resolver.is_prefix("2019-01")
    assert resolver.is_prefix("2019-01-01")
    assert resolver.is_prefix("October")
    assert resolver.is_prefix("October 1")
    assert resolver.is_prefix("October 1, ")

    assert not resolver.is_prefix("Nonsense!")
    assert not resolver.is_prefix("2017 07 19 J")


def test_date_resolver_find_valid(kb):
    resolver = DateResolver(
        tokenizer=WhitespaceTokenizer(),
        normalizer=LatinLowercaseNormalizer(),
        kb=kb,
    )

    expected = [Date(year=2019, month=1, day=1)]
    assert expected == resolver.resolve("2019-01-01")
    assert expected == resolver.resolve("Jan 1st, 2019")
    assert expected == resolver.resolve("01/01/19")
    assert expected == resolver.resolve("2019-JAN-01")


def test_date_resolver_fail_invalid(kb):
    resolver = DateResolver(
        tokenizer=WhitespaceTokenizer(),
        normalizer=LatinLowercaseNormalizer(),
        kb=kb,
    )

    result = resolver.resolve("Nonsense!")
    assert not result

    result = resolver.resolve("2017 07 19 J")
    assert not result

    result = resolver.resolve("3")
    assert not result

    result = resolver.resolve("15t")
    assert not result


def test_default_resolver(kb, apple):
    tokenizer = WhitespaceTokenizer()
    normalizer = LatinLowercaseNormalizer()
    resolver = TermResolver(
        name="default", tokenizer=tokenizer, normalizer=normalizer, kb=kb,
    )
    kb.save_node(apple)

    assert resolver.is_prefix("a")
    assert resolver.is_prefix("apple")
    assert not resolver.is_prefix("b")
    assert not resolver.is_prefix("apple, ink.")

    assert [apple] == resolver.resolve("apple")
    assert [apple] == resolver.resolve("apple, inc.")

    assert not resolver.resolve("banana")
    assert not resolver.resolve("apple, ink.")
    assert not resolver.is_prefix("apple, ink")
