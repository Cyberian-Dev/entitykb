from pydantic.json import pydantic_encoder
from entitykb.models.node import Node, Edge
from entitykb.models.serialization import Envelope, Kind
import json


def test_serialize_node():
    n = Node(data=dict(a=1))

    env_0 = Envelope(n)
    assert env_0.kind == Kind.Node
    assert env_0.payload == n

    s: str = json.dumps(env_0, default=pydantic_encoder)
    d: dict = json.loads(s)
    assert d.keys() == {"kind", "payload"}
    assert d["payload"].keys() == {"label", "key", "data"}

    env_1 = Envelope(d)
    assert env_1.kind == Kind.Node
    assert env_1.payload == n
    assert env_1.payload.data == dict(a=1)
    assert env_1 == env_0


def test_serialize_edge():
    e = Edge(start="a", verb="IS_A", end="b", data=dict(c=2))

    env_0 = Envelope(e)
    assert env_0.kind == Kind.Edge
    assert env_0.payload == e

    s: str = json.dumps(env_0, default=pydantic_encoder)
    d: dict = json.loads(s)
    assert d.keys() == {"kind", "payload"}
    assert d["payload"].keys() == {"start", "verb", "end", "data"}

    env_1 = Envelope(d)
    assert env_1.kind == Kind.Edge
    assert env_1.payload == e
    assert env_1.payload.data == dict(c=2)
    assert env_1 == env_0
