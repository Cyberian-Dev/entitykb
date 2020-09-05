import pytest

from entitykb.graph import (
    Direction,
    Searcher,
    Query,
    SearchResults,
    Entity,
    Graph,
    QB,
)

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

edges = [
    fruit >> "IS_A" >> food,
    apple >> "IS_A" >> fruit,
    granny_smith >> "IS_A" >> apple,
    honeycrisp >> "IS_A" >> apple,
    dessert >> "IS_A" >> food,
    pie >> "IS_A" >> dessert,
    apple_pie >> "IS_A" >> pie,
    apple_pie >> "HAS_A" >> apple,
    apple_sauce >> "IS_A" >> dessert,
    apple_sauce >> "HAS_A" >> apple,
]


@pytest.fixture
def graph():
    graph = Graph()
    assert "<Graph: 0 nodes, 0 edges>" == repr(graph)

    for entity in entities:
        graph.save_node(entity)

    for edge in edges:
        graph.save_edge(edge)

    assert "<Graph: 9 nodes, 10 edges>" == repr(graph)
    return graph


def test_searcher(graph):
    searcher = Searcher(graph=graph)
    query = Query(starts=(apple,), steps=())
    results = searcher.search(query=query)
    assert 1 == len(results)


def test_start_all_goal_all(graph):
    results = Searcher(graph=graph).search(QB(starts=graph).all())
    assert isinstance(results, SearchResults)
    assert 9 == len(results)
    for result in results:
        assert 0 == len(result)
        assert result.start == result.end


def test_start_all_goal_first(graph):
    results = Searcher(graph=graph).search(QB(starts=graph).first())
    assert 1 == len(results)
    assert 0 == len(results[0])
    assert results[0].start == results[0].end


def test_start_one_goal_all(graph):
    results = Searcher(graph=graph).search(QB([apple]).all())

    assert 1 == len(results)
    assert 0 == len(results[0])
    assert results[0].start == results[0].end
    assert apple.key == results[0].end


def test_start_one_walk_passthru_is_a_goal_all(graph):
    query = QB([apple]).walk("is_a").all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        granny_smith.key,
        honeycrisp.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_walk_with_max_hops(graph):
    query = QB([food]).walk("is_a", max_hops=2).all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        fruit.key,
        apple.key,
        dessert.key,
        pie.key,
        apple_sauce.key,
    }
    assert {food.key} == {r.start for r in results}


def test_start_one_walk_incoming_is_a_include_start_goal_all(graph):
    query = QB([apple]).walk("is_a", passthru=True).all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        apple.key,
        granny_smith.key,
        honeycrisp.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_start_one_walk_outgoing_is_a_goal_all(graph):
    query = QB([apple]).walk("is_a", directions=Direction.outgoing).all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        fruit.key,
        food.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_start_one_walk_incoming_all_goal_all(graph):
    query = QB([apple]).walk(directions=Direction.incoming).all()
    results = Searcher(graph=graph).search(query)
    assert {r.end for r in results} == {
        granny_smith.key,
        honeycrisp.key,
        apple_sauce.key,
        apple_pie.key,
    }
    assert {apple.key} == {r.start for r in results}


def test_start_one_walk_every_direction_goal_all(graph):
    query = QB([apple]).walk(directions=None).all()
    results = Searcher(graph=graph).search(query)
    assert 8 == len(results)
    assert apple.key not in {r.end for r in results}
    assert {apple.key} == {r.start for r in results}


def test_start_one_multi_step_walk_goal_all(graph):
    query = (
        QB([apple])
        .walk("has_a")
        .walk("is_a", directions=Direction.outgoing)
        .all()
    )
    results = Searcher(graph=graph).search(query)
    assert 3 == len(results)
    assert {food.key, dessert.key, pie.key} == {r.end for r in results}
    assert {apple.key} == {r.start for r in results}


def test_start_one_filter_label_goal_all(graph):
    query = (
        QB([dessert])
        .walk(directions=Direction.incoming)
        .filter(label="SAUCE")
        .all()
    )
    results = Searcher(graph=graph).search(query)
    assert {apple_sauce.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}


def test_start_one_wall_every_filter_is_a(graph):
    query = (
        QB([apple]).walk("HAS_A", directions=None).filter(is_a=dessert).all()
    )
    results = Searcher(graph=graph).search(query)
    assert {apple_sauce.key, apple_pie.key} == set(results.ends)
    assert {apple.key} == {r.start for r in results}


def test_find_most_relevant(graph):
    query = QB(food, pie, dessert).walk().all()
    entity = Searcher(graph=graph).most_relevant(query)
    assert apple_pie == entity

    query = QB(food, pie, dessert).walk(directions=Direction.outgoing).all()
    entity = Searcher(graph=graph).most_relevant(query)
    assert food == entity

    query = QB(food, pie, dessert).walk(directions=None).all()
    entity = Searcher(graph=graph).most_relevant(query)
    assert apple_pie == entity


def test_find_closest(graph):
    query = QB(granny_smith, honeycrisp, pie).walk().all()
    entity = Searcher(graph=graph).closest(query)
    assert apple_pie == entity

    query = (
        QB(granny_smith, honeycrisp, pie)
        .walk(directions=Direction.outgoing)
        .all()
    )
    entity = Searcher(graph=graph).closest(query)
    assert apple == entity

    query = QB(granny_smith, honeycrisp, pie).walk(directions=None).all()
    entity = Searcher(graph=graph).closest(query)
    assert apple == entity


def test_prefix_text_suggest(graph):
    query = QB(prefix="appl").all()
    results = Searcher(graph=graph).search(query)
    assert set(results.entities) == {apple, apple_pie, apple_sauce}

    query = QB(prefix="appl").filter(is_a="Pie|ENTITY").all()
    results = Searcher(graph=graph).search(query)
    assert set(results.entities) == {apple_pie}

    query = QB(prefix="appl").filter(label="SAUCE").all()
    results = Searcher(graph=graph).search(query)
    assert set(results.entities) == {apple_sauce}


def test_prefix_text_term(graph):
    query = QB(term="appl").all()
    results = Searcher(graph=graph).search(query)
    assert not results.entities

    query = QB(term="apple").all()
    results = Searcher(graph=graph).search(query)
    assert set(results.entities) == {apple}

    query = QB(term="apple pie").all()
    results = Searcher(graph=graph).search(query)
    assert set(results.entities) == {apple_pie}


def test_filter_with_entity_self_ok(graph):
    query = QB(food).walk().filter(is_a=apple).all()
    results = Searcher(graph=graph).search(query)
    assert set(results.entities) == {honeycrisp, granny_smith}

    query = QB(food).walk().filter(is_a=apple, self_ok=True).all()
    results = Searcher(graph=graph).search(query)
    assert set(results.entities) == {honeycrisp, granny_smith, apple}
