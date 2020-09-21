import pytest

from entitykb.graph import (
    A,
    Entity,
    Graph,
    QB,
    Query,
    R,
    SearchResults,
    Searcher,
)

food = Entity(name="Food")
fruit = Entity(name="Fruit")
apple = Entity(name="Apple")
granny_smith = Entity(name="Granny Smith", price=1.99)
honeycrisp = Entity(name="Honeycrisp", price=3.99)
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
    apple_pie >> "KIND_OF" >> pie,
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

    assert "<Graph: 9 nodes, 11 edges>" == repr(graph)
    return graph


def test_searcher(graph):
    query = Query()
    searcher = Searcher(graph=graph, query=query)
    results = searcher.search(apple)
    assert 1 == len(results)
    assert {apple.key} == set(results.ends)

    results = searcher.search(apple.key)
    assert 1 == len(results)
    assert {apple.key} == set(results.ends)


def test_start_all_goal_all(graph):
    query = QB().all()
    results = Searcher(graph=graph, query=query).search(graph)

    assert isinstance(results, SearchResults)
    assert 9 == len(results)
    for result in results:
        assert 0 == len(result)
        assert result.start == result.end


def test_limit_goal(graph):
    query = QB().limit(5)
    results = Searcher(graph=graph, query=query).search(graph)
    assert isinstance(results, SearchResults)
    assert 5 == len(results)


def test_limit_page(graph):
    query = QB().page(2, 2)
    results = Searcher(graph=graph, query=query).search(graph)
    assert isinstance(results, SearchResults)
    assert 2 == len(results)


def test_start_all_goal_first(graph):
    query = QB().first()
    results = Searcher(graph=graph, query=query).search(graph)

    assert 1 == len(results)
    assert 0 == len(results[0])
    assert set(results.starts) == set(results.ends)


def test_start_one_goal_all(graph):
    query = QB().all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert 1 == len(results)
    assert 0 == len(results[0])
    assert set(results.starts) == set(results.ends)
    assert {apple.key} == set(results.ends)


def test_in_nodes(graph):
    query = QB().in_nodes("is_a").all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert {granny_smith.key, honeycrisp.key} == set(results.ends)
    assert {apple.key} == {r.start for r in results}


def test_in_nodes_with_max_hops(graph):
    query = QB().in_nodes("is_a", max_hops=2).all()
    results = Searcher(graph=graph, query=query).search(food)

    assert {
        fruit.key,
        apple.key,
        dessert.key,
        pie.key,
        apple_sauce.key,
    } == set(results.ends)
    assert {food.key} == set(results.starts)


def test_in_nodes_with_passthru(graph):
    query = QB().in_nodes("is_a", passthru=True).all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert {apple.key, granny_smith.key, honeycrisp.key} == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_out_nodes(graph):
    query = QB().out_nodes("is_a").all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert {fruit.key} == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_in_nodes_all_tags(graph):
    query = QB().in_nodes().all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert {
        granny_smith.key,
        honeycrisp.key,
        apple_sauce.key,
        apple_pie.key,
    } == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_all_nodes_all_tags_no_max(graph):
    query = QB().all_nodes(max_hops=None).all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert 8 == len(results)
    assert apple.key not in set(results.ends)
    assert {apple.key} == set(results.starts)


def test_in_has_a_apple_out_is_a(graph):
    query = QB().in_nodes("has_a").out_nodes("is_a").all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert {dessert.key, pie.key} == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_is_keep_label(graph):
    query = QB().in_nodes().keep(A.label == "SAUCE").all()
    results = Searcher(graph=graph, query=query).search(dessert)
    assert {apple_sauce.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}

    query = QB().in_nodes().keep(A.label != "SAUCE").all()
    results = Searcher(graph=graph, query=query).search(dessert)
    assert {pie.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}


def test_is_remove_label(graph):
    query = QB().in_nodes().remove(A.label == "SAUCE").all()
    results = Searcher(graph=graph, query=query).search(dessert)
    assert {pie.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}

    query = QB().in_nodes().remove(A.label != "SAUCE").all()
    results = Searcher(graph=graph, query=query).search(dessert)
    assert {apple_sauce.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}


def test_comparison_options(graph):
    searcher = Searcher(graph=graph, query=None)

    query = QB().in_nodes("is_a").keep(A.price < 3.00).all()
    assert {granny_smith.key} == set(searcher(apple, query=query).ends)

    query = QB().in_nodes("is_a").keep(A.price <= 1.99).all()
    assert {granny_smith.key} == set(searcher(apple, query=query).ends)

    query = QB().in_nodes("is_a").keep(A.price < 1.99).all()
    assert set() == set(searcher(apple, query=query).ends)

    query = QB().in_nodes("is_a").keep(A.price > 3.00).all()
    assert {honeycrisp.key} == set(searcher(apple, query=query).ends)

    query = QB().in_nodes("is_a").keep(A.price >= 3.99).all()
    assert {honeycrisp.key} == set(searcher(apple, query=query).ends)

    query = QB().in_nodes("is_a").keep(A.price > 3.99).all()
    assert set() == set(searcher(apple, query=query).ends)

    query = (
        QB()
        .in_nodes("is_a")
        .keep(A.price > 2.00, A.price < 3.00, all=True)
        .all()
    )
    assert set() == set(searcher(apple, query=query).ends)

    query = (
        QB()
        .in_nodes("is_a")
        .keep(A.price > 2.00, A.price < 3.00, all=False)
        .all()
    )
    assert {honeycrisp.key, granny_smith.key} == set(
        searcher(apple, query=query).ends
    )


def test_has_apple_keep_pies(graph):
    query = QB().in_nodes("HAS_A").keep(R.is_a >> pie).all()
    results = Searcher(graph=graph, query=query).search(apple)

    assert {apple_pie.key} == set(results.ends)
    assert {apple.key} == {r.start for r in results}


def test_keep_what_an_apple_is(graph):
    query = QB().in_nodes(max_hops=3).keep(R.is_a << apple).all()
    results = Searcher(graph=graph, query=query).search(food)
    assert {fruit.key} == set(results.ends)


def test_keep_adjacent_to_pie(graph):
    query = QB().in_nodes(max_hops=3).keep(R.is_a ** pie).all()
    results = Searcher(graph=graph, query=query).search(food)
    assert {dessert.key, apple_pie.key} == set(results.ends)


def test_remove_is_a(graph):
    query = QB().in_nodes("HAS_A").remove(R.IS_A >> pie).all()
    results = Searcher(graph=graph, query=query).search(apple)
    assert {apple_sauce.key} == set(results.ends)


def test_multi_result_hops(graph):
    query = QB().out_nodes("IS_A", max_hops=4).all()
    results = Searcher(graph=graph, query=query).search(apple_pie, apple_sauce)
    assert set(results.ends).issuperset({dessert.key})
