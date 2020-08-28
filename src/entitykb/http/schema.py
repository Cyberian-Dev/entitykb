from typing import List, Union

from pydantic.dataclasses import dataclass
from dataclasses import field

Tag = str
Label = str
Token = str


@dataclass
class DocToken:
    token: Token
    offset: int


@dataclass
class Entity:
    name: str
    label: str
    key: str = None
    synonyms: List[str] = None
    meta: dict = None


@dataclass
class Correction:
    distance: int
    ratio: int


@dataclass
class DocEntity:
    text: str
    tokens: List[DocToken]
    entity: Entity
    entity_key: str
    correction: Correction = None


@dataclass
class Doc:
    text: str
    tokens: List[DocToken]
    entities: List[DocEntity]


@dataclass
class Resource:
    key: str
    uri: str
    title: str
    content: str
    data: dict


Node = Union[Entity, Resource, Label]


@dataclass
class Relationship:
    a: Node
    tag: Tag
    b: Node


@dataclass
class ParseRequest:
    text: str
    labels: List[str] = field(default_factory=list)
