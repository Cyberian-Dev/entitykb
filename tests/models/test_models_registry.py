from entitykb.contrib.date import Date
from entitykb.models import Entity, Node, Registry


class CustomNode(Node):
    pass


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
    registry = Registry.instance()
    schema = registry.create_schema(verbs=[], labels=[])
    schema = schema.dict()
    assert schema.keys() == {"nodes", "labels", "verbs"}

    assert schema.get("nodes").get("NODE") == {
        "properties": {
            "data": {"title": "Data", "type": "object"},
            "key": {"title": "Key", "type": "string"},
            "label": {"title": "Label", "type": "string"},
        },
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
                "items": {},
                "title": "Synonyms",
                "type": "array",
            },
            "year": {"title": "Year", "type": "integer"},
        },
        "title": "Date",
        "type": "object",
    }
