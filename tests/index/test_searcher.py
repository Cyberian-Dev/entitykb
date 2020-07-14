import pytest

from entitykb import Entity
from entitykb.index import QB, Searcher, SearchResults

food = Entity(name="Food")
fruit = Entity(name="Fruit")
apple = Entity(name="Apple")
granny_smith = Entity(name="Granny Smith")
honeycrisp = Entity(name="Honeycrisp")
dessert = Entity(name="Dessert")
pie = Entity(name="Pie")
apple_pie = Entity(name="Apple Pie")
apple_sauce = Entity(name="Apple Sauce", label="SAUCE")

entities = [
    food,
    fruit,
    apple,
    granny_smith,
    honeycrisp,
    dessert,
    pie,
    apple_pie,
    apple_sauce,
]

relationships = [
    fruit.rel.is_a(food),
    apple.rel.is_a(fruit),
    granny_smith.rel.is_a(apple),
    honeycrisp.rel.is_a(apple),
    dessert.rel.is_a(food),
    pie.rel.is_a(dessert),
    apple_pie.rel.is_a(pie),
    apple_pie.rel.has_a(apple),
    apple_sauce.rel.is_a(dessert),
    apple_sauce.rel.has_a(apple),
]


@pytest.fixture
def graph(index):
    """ Must access graph to test func args, see the "food" items added. """

    graph = index.graph
    assert "<Graph: (0 entities)>" == repr(graph)

    for entity in entities:
        index.add_entity(entity)
    for relationship in relationships:
        index.add_relationship(relationship)

    assert "<Graph: (9 entities)>" == repr(graph)
    return graph


def test_start_all_goal_all(graph):
    results = Searcher(graph=graph).search(QB().all())
    assert isinstance(results, SearchResults)
    assert 9 == len(results)
    assert 0 == len(results[0])
    assert results[0].start_id == results[0].end_id


def test_start_all_goal_first(graph):
    results = Searcher(graph=graph).search(QB().first())
    assert 1 == len(results)
    assert 0 == len(results[0])
    assert results[0].start_id == results[0].end_id


def test_start_one_goal_all(graph):
    results = Searcher(graph=graph).search(QB(apple).all())

    assert 1 == len(results)
    assert 0 == len(results[0])
    assert results[0].start_id == results[0].end_id
    assert apple.key == results[0].start


def test_start_one_walk_passthru_is_a_goal_all(graph):
    query = QB(apple).walk("is_a").all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        granny_smith.key,
        honeycrisp.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_start_one_walk_incoming_is_a_include_start_goal_all(graph):
    query = QB(apple).walk("is_a", passthru=True).all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        apple.key,
        granny_smith.key,
        honeycrisp.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_start_one_walk_outcoming_is_a_goal_all(graph):
    query = QB(apple).walk("is_a", incoming=False).all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        fruit.key,
        food.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_start_one_walk_incoming_all_goal_all(graph):
    query = QB(apple).walk(incoming=True).all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        granny_smith.key,
        honeycrisp.key,
        apple_sauce.key,
        apple_pie.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_start_one_walk_every_direction_goal_all(graph):
    query = QB(apple).walk(incoming=None).all()
    results = Searcher(graph=graph).search(query)
    assert 8 == len(results)
    assert apple.key not in {r.end for r in results}
    assert {apple.key} == {r.start for r in results}


def test_start_one_multi_step_walk_goal_all(graph):
    query = QB(apple).walk("has_a").walk("is_a", incoming=False).all()
    results = Searcher(graph=graph).search(query)
    assert 3 == len(results)
    assert {r.end for r in results} == {
        food.key,
        dessert.key,
        pie.key,
    }
    assert {apple.key} == {r.start for r in results}
