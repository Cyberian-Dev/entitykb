from dataclasses import field
from typing import List

from pydantic.dataclasses import dataclass

Tag = str
Label = str
Token = str


@dataclass
class Node:
    label: str = None
    key: str = None
    data: dict = None


@dataclass
class DocToken:
    token: Token
    offset: int


@dataclass
class Entity(Node):
    name: str = None
    synonyms: List[str] = None


@dataclass
class DocEntity:
    text: str
    tokens: List[DocToken]
    entity: Entity
    entity_key: str


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


@dataclass
class Relationship:
    a: Node
    tag: Tag
    b: Node


@dataclass
class SuggestRequest:
    term: str


@dataclass
class ParseRequest:
    text: str
    labels: List[str] = field(default_factory=list)
