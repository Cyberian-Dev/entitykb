from typing import List

import pytest

from entitykb import (
    DefaultSearcher,
    Entity,
    F,
    Graph,
    LatinLowercaseNormalizer,
    T,
    Trail,
    Verb,
)


class Product(Entity):
    price: float


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
    fruit >> Verb.IS_A >> food,
    apple >> Verb.IS_A >> fruit,
    granny_smith >> Verb.IS_A >> apple,
    honeycrisp >> Verb.IS_A >> apple,
    dessert >> Verb.IS_A >> food,
    pie >> Verb.IS_A >> dessert,
    apple_pie >> Verb.IS_A >> pie,
    apple_pie >> Verb.KIND_OF >> pie,
    apple_pie >> Verb.HAS_A >> apple,
    apple_sauce >> Verb.IS_A >> dessert,
    apple_sauce >> Verb.HAS_A >> apple,
]


def ends(trails: List[Trail]):
    return set([t.end for t in trails])


def starts(trails: List[Trail]):
    return set([t.start for t in trails])


@pytest.fixture
def graph(root):
    normalizer = LatinLowercaseNormalizer()
    graph = Graph(root=root, normalizer=normalizer)
    assert "<Graph: 0 nodes, 0 edges>" == repr(graph)

    for entity in entities:
        graph.save_node(entity)

    for edge in edges:
        graph.save_edge(edge)

    graph.reindex()
    assert "<Graph: 9 nodes, 11 edges>" == repr(graph)

    return graph


def test_searcher(graph):
    searcher = DefaultSearcher(graph=graph, traversal=T(), starts=[apple])
    trails = list(searcher)
    assert 1 == len(trails)
    assert {apple.key} == ends(trails)

    searcher = DefaultSearcher(graph=graph, traversal=T(), starts=[apple.key])
    trails = list(searcher)
    assert 1 == len(trails)
    assert {apple.key} == ends(trails)


def test_start_all_goal_all(graph):
    searcher = DefaultSearcher(graph=graph, traversal=T(), starts=graph)
    trails = list(searcher)

    assert 9 == len(trails)
    for result in trails:
        assert 0 == len(result)
        assert result.start == result.end


def test_in_nodes(graph):
    t = T().in_nodes(Verb.IS_A)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert {granny_smith.key, honeycrisp.key} == ends(trails)
    assert {apple.key} == {r.start for r in trails}


def test_in_nodes_with_max_hops(graph):
    t = T().in_nodes(Verb.IS_A, max_hops=2)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[food])
    trails = list(searcher)

    assert {
        fruit.key,
        apple.key,
        dessert.key,
        pie.key,
        apple_sauce.key,
    } == ends(trails)
    assert {food.key} == starts(trails)


def test_in_nodes_with_passthru(graph):
    t = T().in_nodes(Verb.IS_A, passthru=True)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert {apple.key, granny_smith.key, honeycrisp.key} == ends(trails)
    assert {apple.key} == starts(trails)


def test_out_nodes(graph):
    t = T().out_nodes(Verb.IS_A)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert {fruit.key} == ends(trails)
    assert {apple.key} == starts(trails)


def test_in_nodes_all_verbs(graph):
    t = T().in_nodes()
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert {
        granny_smith.key,
        honeycrisp.key,
        apple_sauce.key,
        apple_pie.key,
    } == ends(trails)
    assert {apple.key} == starts(trails)


def test_all_nodes_all_verbs_no_max(graph):
    t = T().all_nodes(max_hops=None)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert {apple.key} == starts(trails)
    assert 22 == len(trails)


def test_all_nodes_optional_attribute(graph):
    t = T().all_nodes(max_hops=None).include(F.price > 3.00)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert 1 == len(trails)
    assert {honeycrisp.key} == ends(trails)

    t = T().all_nodes(max_hops=None).exclude(F.price > 3.00)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert 21 == len(trails)
    assert honeycrisp.key not in ends(trails)


def test_in_has_a_apple_out_is_a(graph):
    t = T().in_nodes(Verb.HAS_A).out_nodes(Verb.IS_A)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert {dessert.key, pie.key} == ends(trails)
    assert {apple.key} == starts(trails)


def test_is_include_label(graph):
    t = T().in_nodes().include(F.label == "SAUCE")
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[dessert])
    trails = list(searcher)

    assert {apple_sauce.key} == {r.end for r in trails}
    assert {dessert.key} == {r.start for r in trails}

    t = T().in_nodes().include(F.label != "SAUCE")
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[dessert])
    trails = list(searcher)

    assert {pie.key} == {r.end for r in trails}
    assert {dessert.key} == {r.start for r in trails}


def test_query_exclude_by_label(graph):
    t = T().in_nodes().exclude(F.label == "SAUCE")
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[dessert])
    trails = list(searcher)

    assert {pie.key} == {r.end for r in trails}
    assert {dessert.key} == {r.start for r in trails}

    t = T().in_nodes().exclude(F.label != "SAUCE")
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[dessert])
    trails = list(searcher)

    assert {apple_sauce.key} == {r.end for r in trails}
    assert {dessert.key} == {r.start for r in trails}


def test_comparison_options(graph):
    t = T().in_nodes(Verb.IS_A).include(F.price < 3.00)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.price <= 1.99)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.price < 1.99)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert set() == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.price > 3.00)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {honeycrisp.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.price >= 3.99)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {honeycrisp.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.price.is_in((3.99, 1.99)))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key, honeycrisp.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.price > 3.99)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert set() == ends(trails)

    t = (
        T()
        .in_nodes(Verb.IS_A)
        .include(F.price > 2.00, F.price < 3.00, all=True)
    )
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert set() == ends(trails)

    t = (
        T()
        .in_nodes(Verb.IS_A)
        .include(F.price > 2.00, F.price < 3.00, all=False)
    )
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {honeycrisp.key, granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.contains("Smith"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.contains("smith"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert set() == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.icontains("SMITH"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).exclude(F.name.iexact("honeycrisp"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).exclude(F.name.startswith("Hone"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).exclude(F.name.istartswith("hone"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.endswith("Smith"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.iendswith("SMITH"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.price.range(1.50, 5))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key, honeycrisp.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.iendswith("SMITH"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {granny_smith.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.regex("^[A-Za-z]*$"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {honeycrisp.key} == ends(trails)

    t = T().in_nodes(Verb.IS_A).include(F.name.iregex(r"^[\w\s]+$"))
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {honeycrisp.key, granny_smith.key} == ends(trails)


def test_has_apple_include_pies(graph):
    t = T().in_nodes(Verb.HAS_A).include(Verb.is_a >> pie)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)

    assert {apple_pie.key} == ends(trails)
    assert {apple.key} == {r.start for r in trails}


def test_include_what_an_apple_is(graph):
    t = T().in_nodes(max_hops=3).include(Verb.is_a << apple)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[food])
    trails = list(searcher)
    assert {fruit.key} == ends(trails)


def test_include_adjacent_to_pie(graph):
    t = T().in_nodes(max_hops=3).include(Verb.is_a ** pie)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[food])
    trails = list(searcher)
    assert {dessert.key, apple_pie.key} == ends(trails)


def test_exclude_is_a(graph):
    t = T().in_nodes(Verb.HAS_A).exclude(Verb.is_a >> pie)
    searcher = DefaultSearcher(graph=graph, traversal=t, starts=[apple])
    trails = list(searcher)
    assert {apple_sauce.key} == ends(trails)


def test_multi_result_hops(graph):
    t = T().out_nodes(Verb.IS_A, max_hops=4)
    searcher = DefaultSearcher(
        graph=graph, traversal=t, starts=(apple_pie, apple_sauce)
    )
    trails = list(searcher)
    assert ends(trails).issuperset({dessert.key})
