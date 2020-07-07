from entitykb import Entity, Graph, Query, Relationship, Tag


apple = Entity(name="Apple", label="FRUIT")
granny_smith = Entity(name="Granny Smith", label="FRUIT")
honeycrisp = Entity(name="Honeycrisp", label="FRUIT")
gs_is_a_apple = Relationship(granny_smith, Tag.IS_A, apple)
hc_is_a_apple = Relationship(honeycrisp, Tag("is_a"), apple)


def test_relationship():
    graph = Graph()
    assert "<Graph: (0 entities, 0 relationships)>" == repr(graph)

    graph.add(apple, granny_smith, honeycrisp, gs_is_a_apple, hc_is_a_apple)
    assert "<Graph: (3 entities, 2 relationships)>" == repr(graph)

    assert graph.q(granny_smith).is_a(apple)
    assert graph.q(honeycrisp).IS_A(apple)
    assert not graph.q(apple).IS_A(honeycrisp)
    assert not graph.q(apple).IS_A(apple)

    assert {gs_is_a_apple} == graph.q(granny_smith).is_a(apple)
