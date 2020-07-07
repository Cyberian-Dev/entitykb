from entitykb import Entity, Graph, Relationship, Tag
import pickle

food = Entity(name="Food")
fruit = Entity(name="Fruit")
apple = Entity(name="Apple")
granny_smith = Entity(name="Granny Smith")
honeycrisp = Entity(name="Honeycrisp")
dessert = Entity(name="Dessert")
pie = Entity(name="Pie")
apple_pie = Entity(name="Apple Pie")

entities = [
    food,
    fruit,
    apple,
    granny_smith,
    honeycrisp,
    dessert,
    pie,
    apple_pie,
]

relationships = [
    Relationship(fruit, Tag.IS_A, food),
    Relationship(apple, Tag.IS_A, fruit),
    Relationship(granny_smith, Tag.IS_A, apple),
    Relationship(honeycrisp, Tag.IS_A, apple),
    Relationship(dessert, Tag.IS_A, food),
    Relationship(pie, Tag.IS_A, dessert),
    Relationship(apple_pie, Tag.IS_A, pie),
    Relationship(apple_pie, Tag.HAS, apple),
]


def test_graph_create_and_query():
    graph = Graph()
    assert "<Graph: (0 entities)>" == repr(graph)

    graph.add(*entities)
    graph.add(*relationships)
    assert "<Graph: (8 entities)>" == repr(graph)

    data = pickle.dumps(graph)
    graph = pickle.loads(data)

    # example node queries
    assert {granny_smith, honeycrisp} == set(graph.q.is_a(apple))
    assert {apple_pie} == set(graph.q.is_a(pie).has(apple))
    assert {apple_pie} == set(graph.q.has(apple).is_a(pie))
    assert {apple, granny_smith, honeycrisp} == set(graph.q.is_a(fruit))
    assert {apple_pie} == set(graph.q.is_a(dessert).has(apple))
    assert {apple_pie} == set(graph.q.is_a(food).has(apple))
    assert set() == set(graph.q.is_a(food).has(granny_smith))
