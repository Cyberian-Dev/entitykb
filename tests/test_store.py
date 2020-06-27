from entitykb import (
    DefaultTokenizer,
    DefaultNormalizer,
    DefaultIndex,
    FindResult,
)

from entitykb.store import TermEntities


def test_not_fuzzy(apple):
    index = DefaultIndex.create(
        "entitykb.DefaultIndex",
        tokenizer=DefaultTokenizer(),
        normalizer=DefaultNormalizer(),
    )

    # add and re-add
    index.add(apple)
    assert 1 == len(index)
    assert 5 == len(index.store.trie), str(list(index.store.trie.keys()))

    index.add(apple)
    assert 1 == len(index)
    assert 5 == len(index.store.trie), str(list(index.store.trie.keys()))

    # reference
    ref = index.store.trie.get("apple")
    assert isinstance(ref, TermEntities)
    assert 1 == len(ref.term_entity_ids)

    # get
    assert apple == index.get(apple.key)

    # is_prefix
    assert index.is_prefix("apple")
    assert index.is_prefix("apple", label_set={"COMPANY", "ANOTHER"})
    assert index.is_prefix("ap")
    assert not index.is_prefix("inc")
    assert not index.is_prefix("apple", label_set={"INVALID", "ANOTHER"})

    # find
    assert FindResult(term="apple", entities=(apple,)) == index.find("apple")
    assert FindResult(term="apple", entities=()) == index.find("apple", {"X"})

    # suggest
    assert ["apple", "apple, inc."] == index.suggest("apple", None)
    assert ["apple"] == index.suggest("apple", None, limit=1)
    assert ["apple", "apple, inc."] == index.suggest("apple", {"COMPANY"})
    assert [] == index.suggest("apple", {"RECORD_COMPANY"})

    # reset
    index.reset()
    assert 0 == len(index.store.trie), str(list(index.store.trie.keys()))
    assert 0 == len(index)

    # info
    assert set(index.info().keys()).issuperset({"entity_count", "nodes_count"})
