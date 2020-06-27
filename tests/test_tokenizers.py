from entitykb.model import Token
from entitykb.tokenizers import Tokenizer, DefaultTokenizer


def test_construct():
    tokenizer = Tokenizer.create()
    assert isinstance(tokenizer, DefaultTokenizer)

    tokenizer = Tokenizer.create(DefaultTokenizer)
    assert isinstance(tokenizer, DefaultTokenizer)

    class_name = "entitykb.tokenizers.DefaultTokenizer"
    tokenizer = Tokenizer.create(class_name)
    assert isinstance(tokenizer, DefaultTokenizer)

    argument = DefaultTokenizer()
    tokenizer = Tokenizer.create(argument)
    assert argument is tokenizer


def test_default_tokenizer():
    tokenizer = Tokenizer.create()

    assert list(tokenizer("one")) == ["one"]

    tokens = list(tokenizer("one two"))
    assert tokens == ["one", "two"]
    assert tokens[0].ws_after
    assert not tokens[1].ws_after

    assert tokenizer.detokenize(tokens) == "one two"
    assert tokenizer.detokenize(tokens[:1]) == "one"
    assert tokenizer.detokenize(tokens[1:]) == "two"

    tokens = list(tokenizer("one two \n"))
    assert tokens == ["one", "two"]
    assert tokens[0].ws_after
    assert tokens[1].ws_after

    assert (("one", False),) == tokenizer.as_tuples("one")
    assert (("one", True), ("two", False)) == tokenizer.as_tuples("one two")
    assert (("isn", False), ("'", False), ("t", False)) == tokenizer.as_tuples(
        "isn't"
    )
    assert (("3", False), (".", False), ("14", False)) == tokenizer.as_tuples(
        "3.14"
    )

    assert (("3", False), (".", True), ("14", False)) == tokenizer.as_tuples(
        "3. 14"
    )

    assert (
        ("a", True),
        ("b", True),
        ("(", False),
        ("c", False),
        (")", False),
    ) == tokenizer.as_tuples("a b (c)")


def test_roundtrip_de_tokenize():
    tokenizer = Tokenizer.create()

    examples = [
        "Strange,",
        '"Starting" quote works.',
        'Ending quote "works"',
        "Sentences with (parens) work as expected.",
        "What!?! Isn't this contraction working?",
        "Here is a - hyphen?",
        "a b (c (d (e))) f",
    ]

    for example in examples:
        tokens = tokenizer(example)
        output = tokenizer.detokenize(tokens)
        assert example == output, f"{example} != {output} [{tokens}]"


def test_detokenize_through_add():
    tokenizer = Tokenizer.create()
    original = "one, 3.14 (a [b] c-d&f)"
    tokens = tokenizer(original)
    count = 0
    concatted = None

    for token in tokens:
        concatted = token if concatted is None else concatted + token
        count += 1

    assert count == 14
    assert isinstance(concatted, Token), f"{type(concatted)}"
    assert original == concatted

    assert concatted.left_token
    while concatted.left_token:
        concatted = concatted.left_token
        count -= 1
    assert count == 1
    assert concatted == "one"
