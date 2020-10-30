from entitykb.models import Registry, Node, Entity, Edge
from entitykb.contrib.date import Date


class CustomNode(Node):
    pass


class IsA(Edge):
    value: int = 9
    __all_tags__ = ("IS_A",)


def test_edge_tags():
    assert Edge.get_all_tags() == set()
    assert IsA.get_all_tags() == {"IS_A"}


def test_edge_create():
    registry = Registry()
    assert isinstance(registry.create(Edge, Edge()), Edge)
    assert isinstance(registry.create(Edge, {}), Edge)
    assert isinstance(registry.create(Edge, tag="HAS_A"), Edge)
    assert isinstance(registry.create(Edge, tag="IS_A"), IsA)

    assert isinstance(registry.create(Edge, {"tag": "IS_A"}), IsA)
    assert isinstance(IsA.create(), IsA)

    assert registry.create(Edge, {"tag": "IS_A"}).value == 9
    assert registry.create(Edge, {"tag": "IS_A", "value": 11}).value == 11


def test_node_create():
    registry = Registry()
    assert isinstance(registry.create(Node, Node()), Node)
    assert isinstance(registry.create(Node, {}), Node)
    assert isinstance(registry.create(Node), Node)
    assert isinstance(registry.create(Node, label="NODE"), Node)
    assert isinstance(registry.create(Entity, label="NODE"), Node)

    assert isinstance(
        registry.create(Entity, name="abc", label="ENTITY"), Entity
    )
    assert isinstance(registry.create(Entity, name="abc"), Entity)

    assert isinstance(registry.create(CustomNode, {}), CustomNode)
    assert isinstance(registry.create(Node, label="CUSTOM_NODE"), CustomNode)


def test_round_trip_create():
    custom_node = CustomNode()
    data = custom_node.dict()

    registry = Registry()
    roundtrip = registry.create(Node, data)

    assert roundtrip.key == custom_node.key
    assert isinstance(roundtrip, CustomNode), f"Fail: {data} => {roundtrip}"


def test_node_lookup():
    lookup = Registry.instance().lookup
    assert {"NODE", "ENTITY", "DATE"}.issubset(lookup.nodes.keys())

    assert Node == lookup.get_node_class(Node, {})
    assert Date == lookup.get_node_class(Date, {})
    assert Date == lookup.get_node_class(Node, dict(label="DATE"))
    assert Entity == lookup.get_node_class(Node, dict(label="ENTITY"))
    assert Entity == lookup.get_node_class(Node, dict(label="XYZ", name="abc"))


def test_schema():
    schema = Registry.instance().schema.dict()
    assert schema.keys() == {"nodes", "edges"}

    assert schema.get("edges").get("EDGE") == {
        "properties": {
            "data": {"title": "Data", "type": "object"},
            "end": {"title": "End", "type": "string"},
            "start": {"title": "Start", "type": "string"},
            "tag": {"title": "Tag", "type": "string"},
            "weight": {"default": 1, "title": "Weight", "type": "integer"},
        },
        "title": "Edge",
        "type": "object",
    }

    assert schema.get("nodes").get("NODE") == {
        "properties": {
            "data": {"title": "Data", "type": "object"},
            "key": {"title": "Key", "type": "string"},
            "label": {"title": "Label", "type": "string"},
        },
        "required": ["label"],
        "title": "Node",
        "type": "object",
    }

    assert schema.get("nodes").get("DATE") == {
        "properties": {
            "data": {"title": "Data", "type": "object"},
            "day": {"title": "Day", "type": "integer"},
            "key": {"title": "Key", "type": "string"},
            "label": {"title": "Label", "type": "string"},
            "month": {"title": "Month", "type": "integer"},
            "name": {"title": "Name", "type": "string"},
            "synonyms": {
                "default": (),
                "items": {"type": "string"},
                "title": "Synonyms",
                "type": "array",
            },
            "year": {"title": "Year", "type": "integer"},
        },
        "required": ["label"],
        "title": "Date",
        "type": "object",
    }
