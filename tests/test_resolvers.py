from entitykb import (
    DefaultResolver,
    Resolver,
    DefaultNormalizer,
    DefaultTokenizer,
    DefaultIndex,
)
from entitykb.date import DateResolver, Date


def test_resolver_construct():
    tokenizer = DefaultTokenizer()
    normalizer = DefaultNormalizer()
    index = DefaultIndex(tokenizer=tokenizer, normalizer=normalizer)

    assert isinstance(
        Resolver.create(
            None,
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            index=index,
        ),
        DefaultResolver,
    )

    assert isinstance(
        Resolver.create(
            DefaultResolver,
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            index=index,
        ),
        DefaultResolver,
    )

    assert isinstance(
        Resolver.create(
            DateResolver,
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            index=index,
        ),
        DateResolver,
    )

    assert isinstance(
        Resolver.create(
            "entitykb.date.DateResolver",
            name="default",
            tokenizer=tokenizer,
            normalizer=normalizer,
            index=index,
        ),
        DateResolver,
    )


def test_date_resolver_is_prefix():
    resolver = DateResolver(
        tokenizer=DefaultTokenizer(), normalizer=DefaultNormalizer()
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


def test_date_resolver_find_valid():
    resolver = DateResolver(
        tokenizer=DefaultTokenizer(), normalizer=DefaultNormalizer()
    )

    result = resolver.find("2019-01-01")
    assert result
    assert result.entity_keys == ("2019-01-01|DATE",)
    assert result.entities[0] == Date(year=2019, month=1, day=1)

    result = resolver.find("Jan 1st, 2019")
    assert str(result) == "Jan 1st, 2019 [2019-01-01|DATE]"

    result = resolver.find("01/01/19")
    assert str(result) == "01/01/19 [2019-01-01|DATE]"

    result = resolver.find("2019-JAN-01")
    assert str(result) == "2019-JAN-01 [2019-01-01|DATE]"


def test_date_resolver_fail_invalid():
    resolver = DateResolver(
        tokenizer=DefaultTokenizer(), normalizer=DefaultNormalizer()
    )

    result = resolver.find("2019-01-01", label_set={"NOT_DATE"})
    assert not result

    result = resolver.find("Nonsense!")
    assert not result

    result = resolver.find("2017 07 19 J")
    assert not result

    result = resolver.find("3")
    assert not result

    result = resolver.find("15t")
    assert not result


def test_default_resolver(apple):
    tokenizer = DefaultTokenizer()
    normalizer = DefaultNormalizer()
    index = DefaultIndex(tokenizer=tokenizer, normalizer=normalizer)
    resolver = DefaultResolver(
        name="default",
        tokenizer=tokenizer,
        normalizer=normalizer,
        index=index,
    )
    resolver.index.add(apple)

    assert resolver.is_prefix("a")
    assert resolver.is_prefix("apple")
    assert not resolver.is_prefix("b")
    assert not resolver.is_prefix("apple, ink.")

    assert (apple,) == resolver.find("apple").entities
    assert (apple,) == resolver.find("apple, inc.").entities

    assert not resolver.find("banana").entities
    assert not resolver.find("apple, ink.").entities
    assert not resolver.is_prefix("apple, ink")
