from entitykb import Entity, Graph, Relationship, Tag, Q, Query
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
    Relationship(apple_pie, Tag.HAS_A, apple),
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
    assert {granny_smith, honeycrisp} == set(graph(Q.is_a(apple)))
    assert {apple_pie} == set(graph(Q.is_a(pie).has_a(apple)))
    assert {apple_pie} == set(graph(Q.has_a(apple).is_a(pie)))
    assert {apple, granny_smith, honeycrisp} == set(graph(Q.is_a(fruit)))
    assert {apple_pie} == set(graph(Q.is_a(dessert).has_a(apple)))
    assert {apple_pie} == set(graph(Q.is_a(food).has_a(apple)))
    assert set() == set(graph(Q.is_a(food).has_a(granny_smith)))


def test_model_query():
    assert Q.is_a == Q(tags=["IS_A"])
    assert Q.is_a(apple) == Q(tags=["IS_A"], entities=[apple])
    assert Q.is_a(apple, incoming=False) == Q(
        tags=["IS_A"], entities=[apple], incoming=False
    )
    assert Q.is_a(apple, hops=2) == Q(tags=["IS_A"], entities=[apple], hops=2)
    assert 1 == len(Q.is_a(apple))

    q = Q.is_a(pie).has_a(apple)
    assert Query(q) == Query(Q.is_a(pie), Q.has_a(apple))
    assert Query(q) == Query.convert(q)
