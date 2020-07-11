import pickle

import pytest

from entitykb import (
    DocEntity,
    Entity,
    Tag,
    Q,
)
from entitykb.index import HAS_LABEL

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
    """ Must access graph to test func args, see the "food" items addded. """

    graph = index.graph
    assert "<Graph: (0 entities)>" == repr(graph)

    for entity in entities:
        index.add_entity(entity)
    for relationship in relationships:
        index.add_relationship(relationship)

    assert "<Graph: (9 entities)>" == repr(graph)
    return graph


def test_pickle_load(graph):
    data = pickle.dumps(graph)
    graph = pickle.loads(data)
    assert "<Graph: (9 entities)>" == repr(graph)


def test_is_a_apple(graph):
    others = graph.get_relationships(Tag.IS_A, True, apple)
    assert 2 == len(others)
    assert {granny_smith, honeycrisp} == set(map(graph.get_entity, others))


def test_is_a_apple_outcoming(graph):
    others = graph.get_relationships(Tag.IS_A, False, apple)
    assert 1 == len(others)
    assert {fruit} == set(map(graph.get_entity, others))


def test_is_a_apple_either_direction(graph):
    others = graph.get_relationships(Tag.IS_A, entity=apple)
    assert 3 == len(others)
    assert {fruit, granny_smith, honeycrisp} == set(
        map(graph.get_entity, others)
    )


def test_is_a_incoming_dict(graph):
    rels = graph.get_relationships(Tag.IS_A, True)
    assert isinstance(rels, dict)
    assert 5 == len(rels)


def test_has_label(graph):
    others = graph.get_relationships(HAS_LABEL, True, "SAUCE")
    assert 1 == len(others)
    assert {apple_sauce} == set(map(graph.get_entity, others))


def test_query_is_a(index, graph):
    assert {granny_smith, honeycrisp} == set(index(Q.is_a(apple)))
    assert {apple, granny_smith, honeycrisp} == set(index(Q.is_a(fruit)))

    assert {apple_pie} == set(index(Q.has_a(apple).is_a(pie)))
    assert {apple_pie} == set(index(Q.is_a(pie).has_a(apple)))


def test_query_is_a_and_has_a(index, graph):
    assert {apple_pie, apple_sauce} == set(index(Q.is_a(dessert).has_a(apple)))
    assert {apple_pie, apple_sauce} == set(index(Q.is_a(food).has_a(apple)))
    assert set() == set(index(Q.is_a(food).has_a(granny_smith)))


def test_query_with_label(index, graph):
    assert {apple_sauce} == set(index(Q.is_a(food).has_label("SAUCE")))
    assert {apple_sauce} == set(
        index(Q.is_a(food).has_a(apple).has_label("SAUCE"))
    )


def test_query_limit_hops(index, graph):
    assert 8 == len(set(index(Q.is_a(food))))
    assert 2 == len(set(index(Q.is_a(food, hops=1))))


def test_entity_ids_keys_and_doc_entities(index, graph):
    assert {granny_smith, honeycrisp} == set(index(Q.is_a("Apple|ENTITY")))
    assert {granny_smith, honeycrisp} == set(
        index(Q.is_a(DocEntity(text=None, doc=None, entity=apple)))
    )
    assert {granny_smith, honeycrisp} == set(
        index(Q.is_a(index.get_entity(apple)))
    )


def test_is_outcoming_direction(index, graph):
    assert {fruit, food} == set(index(Q.is_a(apple, incoming=False)))
    assert {fruit} == set(index(Q.is_a(apple, incoming=False).is_a(food)))
