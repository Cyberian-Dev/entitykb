from entitykb import SearchRequest, T, Direction, F, Comparison


def test_roundtrip():
    request = SearchRequest(traversal=T().in_nodes().include(F.label == "A"))

    data = request.dict()
    assert data == {
        "q": None,
        "keys": [],
        "labels": [],
        "limit": 100,
        "offset": 0,
        "traversal": [
            {
                "directions": [Direction.incoming],
                "max_hops": 1,
                "passthru": False,
                "verbs": [],
            },
            {
                "all": False,
                "criteria": [
                    {
                        "compare": Comparison.exact,
                        "field": "label",
                        "type": "field",
                        "value": "A",
                    }
                ],
                "exclude": False,
            },
        ],
    }

    assert SearchRequest(**data).dict() == data
