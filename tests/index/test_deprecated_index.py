def test_get_entity(index, apple):
    index.save_entity(apple)
    entity_id = index.get_entity(apple)
    assert apple == index.get_entity(entity_id)
    assert apple == index.get_entity(apple.key)


def test_add_again(index, apple):
    index.save_entity(apple)
    entity_id = index.graph.get_node_id(apple)
    assert entity_id == index.save_entity(apple)
    assert 2 == len(index.graph)
    assert 3 == len(index.terms)


def test_is_prefix(index, apple):
    index.save_entity(apple)
    assert index.is_prefix("apple")
    assert index.is_prefix("apple", labels={"COMPANY", "ANOTHER"})
    assert index.is_prefix("ap")
    assert not index.is_prefix("inc")
    assert not index.is_prefix("apple", labels={"INVALID", "ANOTHER"})


def test_find(index, apple):
    index.save_entity(apple)
    assert [apple] == list(index.find("apple"))
    assert set() == set(index.find("apple", labels={"INVALID"}))


def test_suggest(index, apple):
    index.save_entity(apple)
    assert ["Apple, Inc."] == index.suggest("apple")
    assert ["Apple, Inc."] == index.suggest("apple", limit=1)
    assert ["Apple, Inc."] == index.suggest("apple", labels={"COMPANY"})
    assert [] == index.suggest("apple", labels={"RECORD_COMPANY"})
    assert [] == index.suggest("apple", limit=0)
    assert [] == index.suggest("apple", labels={"COMPANY"}, limit=0)
