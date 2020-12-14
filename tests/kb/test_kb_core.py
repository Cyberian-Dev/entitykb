import pytest

from entitykb import KB, Doc, Edge, SearchRequest, T, SearchResponse


def test_parse(kb: KB):
    doc = kb.parse("This is a doc")
    assert isinstance(doc, Doc)
    assert 4 == len(doc.tokens)


def test_creates_files(root, kb: KB, apple):
    assert (root / "config.json").is_file()
    assert (root / "nodes").is_dir()
    assert (root / "edges").is_dir()
    assert not (root / "nodes.dawg").is_file()
    assert not (root / "edges.dawg").is_file()

    kb.reindex()
    assert (root / "nodes.dawg").is_file()
    assert (root / "edges.dawg").is_file()


def test_save_entity(kb: KB, apple, apple_records):
    kb.save_node(apple)
    kb.save_node(apple_records)
    assert {apple, apple_records} == set(kb)

    kb.reindex()

    assert (kb.parse("AAPL")).spans[0].entity == apple
    assert (kb.parse("Apple, Inc.")).spans[0].entity == apple
    assert (kb.parse("Apple Computers")).spans[0].text == "Apple"
    assert (kb.parse("Apple Records")).spans[0].entity == apple_records
    assert 2 == len((kb.parse("Apple")).spans)

    apple2 = apple.copy(update=dict(synonyms=("Apple", "Apple Computers")))

    # should reset the terms
    kb.save_node(apple2)
    kb.reindex()

    assert not (kb.parse("AAPL")).spans
    assert (kb.parse("Apple, Inc.")).spans[0].entity == apple2
    assert (kb.parse("Apple Computers")).spans[0].entity == apple2
    assert (kb.parse("Apple Computers")).spans[0].text == "Apple Computers"
    assert 2 == len((kb.parse("Apple")).spans)

    kb.remove_node(apple2)
    kb.reindex()

    assert 1 == len((kb.parse("Apple")).spans)
    assert 1 == len((kb.parse("Apple Computers")).spans)
    assert (kb.parse("Apple Computers")).spans[0].text == "Apple"


def test_save_load_sync(root, kb: KB, apple):
    def check():
        assert (kb.parse("AAPL")).spans[0].entity == apple
        assert (kb.parse("Apple, Inc.")).spans[0].entity == apple
        assert (kb.parse("Apple,Inc.")).spans[0].entity == apple

    kb.save_node(apple)
    kb.reindex()
    check()

    kb = KB(root=root)
    check()
    kb.reload()
    check()


def test_save_for_entity_and_edge(kb: KB, apple, google):
    assert apple == kb.save(apple)
    assert google == kb.save(google)
    kb.reindex()

    assert 2 == len(kb)
    assert apple == kb.get_node(apple.key)

    kb.connect(start=apple, verb="IS_A", end=apple)
    kb.reindex()

    assert kb.info()["graph"] == {
        "nodes": 2,
        "edges": 1,
    }

    kb.save(Edge(start=apple, verb="POINTS_NO_WHERE", end="INVALID|THING"))
    kb.save(Edge(start=apple, verb="POINTS_NO_WHERE", end=google))
    kb.reindex()

    assert kb.info()["graph"] == {
        "nodes": 2,
        "edges": 3,
    }

    t = T().all_nodes(passthru=True)
    response = kb.search(request=SearchRequest(q="a", traversal=t))
    assert 3 == len(response.nodes)

    kb.remove_node(apple.key)
    kb.reindex()

    assert kb.info()["graph"] == {
        "nodes": 1,
        "edges": 3,
    }

    kb.clean_edges()

    assert kb.info()["graph"] == {
        "nodes": 1,
        "edges": 0,
    }

    data = response.dict()
    compare = SearchResponse(**data)
    assert compare.nodes == response.nodes


def test_kb_save_bool_clear(kb: KB, apple):
    assert bool(kb)

    assert apple == kb.save(apple)
    kb.reindex()

    assert 1 == len(kb)
    kb.clear()

    assert 0 == len(kb)
    assert bool(kb)


def test_kb_save_invalid(kb: KB):
    with pytest.raises(RuntimeError):
        kb.save("invalid!")


def test_get_schema(kb: KB):
    schema = kb.get_schema()
    assert schema.keys() == {"nodes", "verbs", "labels"}
    assert {"NODE", "ENTITY"}.issubset(schema["nodes"].keys())


def test_search_with_results(kb: KB, apple, google):
    kb.save_node(apple)
    kb.save_node(google)
    kb.reindex()

    # default (all nodes, no filter, etc.)
    response = kb.search(request=SearchRequest())
    assert [apple, google] == response.nodes

    # offset = 1, skips 1 node
    response = kb.search(request=SearchRequest(offset=1))
    assert [google] == response.nodes

    # limit = 1
    response = kb.search(request=SearchRequest(limit=1))
    assert [apple] == response.nodes

    # prefix
    request = SearchRequest(q="a")
    response = kb.search(request=request)
    assert [apple] == response.nodes

    # keys
    request = SearchRequest(keys=["Apple, Inc.|COMPANY"])
    response = kb.search(request=request)
    assert [apple] == response.nodes

    # keys
    request = SearchRequest(keys=[apple.key, apple.key, "junk"])
    response = kb.search(request=request)
    assert [apple] == response.nodes

    # labels
    request = SearchRequest(labels=["COMPANY"])
    response = kb.search(request=request)
    assert 2 == len(response.nodes)

    # keys + labels
    request = SearchRequest(keys=["Apple, Inc.|COMPANY"], labels=["COMPANY"])
    response = kb.search(request=request)
    assert [apple] == response.nodes

    # dict
    assert response.dict() == {
        "nodes": [
            {
                "data": None,
                "headquarters": {
                    "city": "Cupertino",
                    "data": None,
                    "key": "1",
                    "label": "LOCATION",
                },
                "key": "Apple, Inc.|COMPANY",
                "label": "COMPANY",
                "name": "Apple, Inc.",
                "synonyms": ("Apple", "AAPL"),
            }
        ],
        "trails": [
            {
                "end": "Apple, Inc.|COMPANY",
                "hops": [],
                "start": "Apple, Inc.|COMPANY",
            }
        ],
    }


def test_search_no_results(kb: KB, apple):
    request = SearchRequest(q="invalid")
    response = kb.search(request=request)
    assert [] == response.nodes

    request = SearchRequest(keys=["Apple, Inc.|COMPANY"], labels=["INVALID"])
    response = kb.search(request=request)
    assert [] == response.nodes

    request = SearchRequest(labels=["INVALID"])
    response = kb.search(request=request)
    assert [] == response.nodes

    request = SearchRequest(limit=0)
    response = kb.search(request=request)
    assert [] == response.nodes


def test_search_with_just_text(kb: KB, apple, google):
    kb.save_node(apple)
    kb.save_node(google)
    kb.reindex()

    response = kb.search("ap")
    assert 1 == len(response)
    assert [apple] == response.nodes
    assert apple == response[0]
    assert [apple] == list(response)
