from entitykb import (
    Comparison,
    Direction,
    F,
    SearchRequest,
    T,
    NeighborRequest,
    Node,
)


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
                "skip_limit": 1000,
            },
        ],
    }

    assert SearchRequest(**data).dict() == data


def test_edge_request():
    node = Node()
    # noinspection PyTypeChecker
    request = NeighborRequest(node_key=node)
    assert request.node_key == node.key
