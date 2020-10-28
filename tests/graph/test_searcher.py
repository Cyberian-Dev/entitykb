import pytest

from entitykb.graph import InMemoryGraph, SearchResults, Searcher
from entitykb.models import Entity, Query, QB, A, R


class Product(Entity):
    __slots__ = ["key", "label", "data", "name", "synonyms", "price"]

    def __init__(self, *, price: float, **kwargs):
        self.price = price
        super().__init__(**kwargs)


food = Entity(name="Food")
fruit = Entity(name="Fruit")
apple = Entity(name="Apple")
granny_smith = Product(name="Granny Smith", price=1.99)
honeycrisp = Product(name="Honeycrisp", price=3.99)
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
    graph = InMemoryGraph()
    assert "<Graph: 0 nodes, 0 edges>" == repr(graph)

    for entity in entities:
        graph.save_node(entity)

    for edge in edges:
        graph.save_edge(edge)

    assert "<Graph: 9 nodes, 11 edges>" == repr(graph)
    return graph


@pytest.fixture
def searcher(graph):
    return Searcher(graph=graph)


def test_searcher(searcher):
    query = Query()
    results = searcher.search(query, apple)
    assert 1 == len(results)
    assert {apple.key} == set(results.ends)

    results = searcher.search(query, apple.key)
    assert 1 == len(results)
    assert {apple.key} == set(results.ends)


def test_start_all_goal_all(searcher, graph):
    query = QB().all()
    results = searcher.search(query, graph)

    assert isinstance(results, SearchResults)
    assert 9 == len(results)
    for result in results:
        assert 0 == len(result)
        assert result.start == result.end


def test_limit_goal(searcher, graph):
    query = QB().limit(5)
    results = searcher.search(query, graph)
    assert isinstance(results, SearchResults)
    assert 5 == len(results)


def test_limit_page(searcher, graph):
    query = QB().page(2, 2)
    results = searcher.search(query, graph)
    assert isinstance(results, SearchResults)
    assert 2 == len(results)


def test_start_all_goal_first(searcher, graph):
    query = QB().first()
    results = searcher.search(query, graph)

    assert 1 == len(results)
    assert 0 == len(results[0])
    assert set(results.starts) == set(results.ends)


def test_start_one_goal_all(searcher, graph):
    query = QB().all()
    results = searcher.search(query, apple)

    assert 1 == len(results)
    assert 0 == len(results[0])
    assert set(results.starts) == set(results.ends)
    assert {apple.key} == set(results.ends)


def test_in_nodes(searcher, graph):
    query = QB().in_nodes("is_a").all()
    results = searcher.search(query, apple)

    assert {granny_smith.key, honeycrisp.key} == set(results.ends)
    assert {apple.key} == {r.start for r in results}


def test_in_nodes_with_max_hops(searcher, graph):
    query = QB().in_nodes("is_a", max_hops=2).all()
    results = searcher.search(query, food)

    assert {
        fruit.key,
        apple.key,
        dessert.key,
        pie.key,
        apple_sauce.key,
    } == set(results.ends)
    assert {food.key} == set(results.starts)


def test_in_nodes_with_passthru(searcher, graph):
    query = QB().in_nodes("is_a", passthru=True).all()
    results = searcher.search(query, apple)

    assert {apple.key, granny_smith.key, honeycrisp.key} == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_out_nodes(searcher):
    query = QB().out_nodes("is_a").all()
    results = searcher.search(query, apple)

    assert {fruit.key} == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_in_nodes_all_tags(searcher, graph):
    query = QB().in_nodes().all()
    results = searcher.search(query, apple)

    assert {
        granny_smith.key,
        honeycrisp.key,
        apple_sauce.key,
        apple_pie.key,
    } == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_all_nodes_all_tags_no_max(searcher):
    query = QB().all_nodes(max_hops=None).all()
    results = searcher.search(query, apple)

    assert 8 == len(results)
    assert apple.key not in set(results.ends)
    assert {apple.key} == set(results.starts)


def test_in_has_a_apple_out_is_a(searcher):
    query = QB().in_nodes("has_a").out_nodes("is_a").all()
    results = searcher.search(query, apple)

    assert {dessert.key, pie.key} == set(results.ends)
    assert {apple.key} == set(results.starts)


def test_is_include_label(searcher):
    query = QB().in_nodes().include(A.label == "SAUCE").all()
    results = searcher.search(query, dessert)
    assert {apple_sauce.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}

    query = QB().in_nodes().include(A.label != "SAUCE").all()
    results = searcher.search(query, dessert)
    assert {pie.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}


def test_query_exclude_by_label(searcher):
    query = QB().in_nodes().exclude(A.label == "SAUCE").all()
    results = searcher.search(query, dessert)
    assert {pie.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}

    query = QB().in_nodes().exclude(A.label != "SAUCE").all()
    results = searcher.search(query, dessert)
    assert {apple_sauce.key} == {r.end for r in results}
    assert {dessert.key} == {r.start for r in results}


def test_comparison_options(searcher):
    query = QB().in_nodes("is_a").include(A.price < 3.00).all()
    assert {granny_smith.key} == set(searcher(query, apple).ends)

    query = QB().in_nodes("is_a").include(A.price <= 1.99).all()
    assert {granny_smith.key} == set(searcher(query, apple).ends)

    query = QB().in_nodes("is_a").include(A.price < 1.99).all()
    assert set() == set(searcher(query, apple).ends)

    query = QB().in_nodes("is_a").include(A.price > 3.00).all()
    assert {honeycrisp.key} == set(searcher(query, apple).ends)

    query = QB().in_nodes("is_a").include(A.price >= 3.99).all()
    assert {honeycrisp.key} == set(searcher(query, apple).ends)

    query = QB().in_nodes("is_a").include(A.price > 3.99).all()
    assert set() == set(searcher(query, apple).ends)

    query = (
        QB()
        .in_nodes("is_a")
        .include(A.price > 2.00, A.price < 3.00, all=True)
        .all()
    )
    assert set() == set(searcher(query, apple).ends)

    query = (
        QB()
        .in_nodes("is_a")
        .include(A.price > 2.00, A.price < 3.00, all=False)
        .all()
    )
    assert {honeycrisp.key, granny_smith.key} == set(
        searcher(query, apple).ends
    )


def test_has_apple_include_pies(searcher):
    query = QB().in_nodes("HAS_A").include(R.is_a >> pie).all()
    results = searcher.search(query, apple)

    assert {apple_pie.key} == set(results.ends)
    assert {apple.key} == {r.start for r in results}


def test_include_what_an_apple_is(searcher):
    query = QB().in_nodes(max_hops=3).include(R.is_a << apple).all()
    results = searcher.search(query, food)
    assert {fruit.key} == set(results.ends)


def test_include_adjacent_to_pie(searcher):
    query = QB().in_nodes(max_hops=3).include(R.is_a ** pie).all()
    results = searcher.search(query, food)
    assert {dessert.key, apple_pie.key} == set(results.ends)


def test_exclude_is_a(searcher):
    query = QB().in_nodes("HAS_A").exclude(R.IS_A >> pie).all()
    results = searcher.search(query, apple)
    assert {apple_sauce.key} == set(results.ends)


def test_multi_result_hops(searcher):
    query = QB().out_nodes("IS_A", max_hops=4).all()
    results = searcher.search(query, apple_pie, apple_sauce)
    assert set(results.ends).issuperset({dessert.key})
