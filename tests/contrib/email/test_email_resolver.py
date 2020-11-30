from entitykb.contrib.email import EmailResolver, Email

resolver = EmailResolver()


def test_is_relevant():
    assert EmailResolver.is_relevant(None)
    assert EmailResolver.is_relevant([])
    assert EmailResolver.is_relevant(["DATE", "EMAIL"])
    assert not EmailResolver.is_relevant(["DATE"])


def test_is_prefix():
    assert resolver.is_prefix("first")
    assert resolver.is_prefix("first.")
    assert resolver.is_prefix("first.last")
    assert resolver.is_prefix("first.last@")
    assert resolver.is_prefix("first.last@domain")
    assert resolver.is_prefix("first.last@domain.")
    assert resolver.is_prefix("first.last@domain.com")
    assert resolver.is_prefix("first.last@sub.domain.com")


def test_is_not_prefix():
    assert not resolver.is_prefix("@")
    assert not resolver.is_prefix(" ")
    assert not resolver.is_prefix("word ")
    assert not resolver.is_prefix("word@ ")
    assert not resolver.is_prefix("word@domain ")


def test_resolve():
    entities = resolver.resolve("username@gmail.com")
    assert 1 == len(entities)

    entity = entities[0]
    assert isinstance(entity, Email)
    assert "username@gmail.com" == entity.name
    assert "EMAIL" == entity.label
    assert "username" == entity.username
    assert "gmail.com" == entity.domain

    entities = resolver.resolve("my.user-name@subsub.sub.domain.tld")
    assert 1 == len(entities)

    entity = entities[0]
    assert "my.user-name@subsub.sub.domain.tld" == entity.name
    assert isinstance(entity, Email)
    assert "EMAIL" == entity.label
    assert "my.user-name" == entity.username
    assert "subsub.sub.domain.tld" == entity.domain


def test_no_resolve():
    assert not resolver.resolve("username@")
    assert not resolver.resolve("username")
    assert not resolver.resolve("username@gmail")
    assert not resolver.resolve("username@gmail.")
    assert not resolver.resolve("username@gmail.com.")
