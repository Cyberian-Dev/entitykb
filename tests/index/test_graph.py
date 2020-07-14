import pickle

import pytest

from entitykb import Entity, Tag
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


def convert(graph, others):
    converted = set()
    for other_id, tag in others:
        converted.add(graph.get_entity(other_id))
    return converted


def test_is_a_apple(graph):
    others = graph.iterate_all_relationships(
        tags=Tag.IS_A, incoming=True, entities=apple
    )
    others = convert(graph, others)
    assert {granny_smith, honeycrisp} == others


def test_is_a_apple_outcoming(graph):
    others = graph.iterate_all_relationships(
        tags=Tag.IS_A, incoming=False, entities=apple
    )
    others = convert(graph, others)
    assert {fruit} == others


def test_is_a_apple_either_direction(graph):
    others = graph.iterate_all_relationships(
        tags=Tag.IS_A, incoming=None, entities=apple
    )
    others = convert(graph, others)
    assert {fruit, granny_smith, honeycrisp} == others


def test_is_a_incoming_dict(graph):
    others = graph.iterate_all_relationships(
        tags=Tag.IS_A, incoming=None, entities=None
    )
    others = convert(graph, others)
    assert 9 == len(others)


def test_has_label(graph):
    others = graph.iterate_all_relationships(
        tags=HAS_LABEL, incoming=True, entities="SAUCE"
    )
    others = convert(graph, others)
    assert {apple_sauce} == others
