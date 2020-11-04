from __future__ import annotations

from typing import Tuple, Optional, Any, List

from pydantic import BaseModel

from .entity import Entity
from .registry import Registry


class Token(str):
    @property
    def ws_after(self) -> bool:
        return getattr(self, "_ws_after", False)

    @ws_after.setter
    def ws_after(self, value: bool):
        setattr(self, "_ws_after", value)

    @property
    def left_token(self) -> Optional["Token"]:
        return getattr(self, "_left_token", None)

    @left_token.setter
    def left_token(self, value: "Token"):
        setattr(self, "_left_token", value)

    def __add__(self, other: "Token") -> "Token":
        data = str(self)
        if self.ws_after:
            data += " "
        data += other
        new_token = Token(data)
        new_token.ws_after = other.ws_after
        new_token.left_token = self
        return new_token


class HasTokens(BaseModel):
    text: str
    tokens: Tuple[DocToken, ...]

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]

    @property
    def offset(self):
        return self.tokens[0].offset

    @property
    def last_offset(self):
        return self.tokens[-1].offset

    @property
    def offsets(self) -> Tuple[int, ...]:
        return tuple(t.offset for t in self.tokens)

    @property
    def num_tokens(self):
        return len(self.tokens)


class DocToken(BaseModel):
    token: Token
    offset: int

    def __str__(self):
        return self.token

    def __repr__(self):
        return f"{self.token} [offset: {self.offset}]"


class DocEntity(HasTokens):
    entity_key: str
    tokens: Tuple[DocToken, ...]
    entity: Entity = None

    def __init__(self, **data: Any):
        entity = Registry.instance().create(Entity, data.get("entity"))
        data.setdefault("entity_key", entity and entity.key)
        super().__init__(**data)

    def __str__(self):
        return f"{self.text} [{self.entity_key}]"

    def __lt__(self, other: "DocEntity"):
        return self.sort_order < other.sort_order

    @property
    def name(self):
        return self.entity and self.entity.name

    @property
    def label(self):
        return self.entity and (self.entity.label or "ENTITY")

    @property
    def is_match_exact(self):
        return self.name == self.text

    @property
    def is_lower_match(self):
        return self.name and (self.name.lower() == self.text.lower())

    @property
    def sort_order(self):
        return (
            -self.num_tokens,
            0 if self.is_match_exact else 1,
            0 if self.is_lower_match else 1,
            self.offset,
            self.label,
        )


class Doc(HasTokens):
    text: str
    entities: Tuple[DocEntity, ...] = None
    tokens: Tuple[DocToken, ...] = None


class ParseRequest(BaseModel):
    text: str
    pipeline: str = "default"
    labels: List[str] = []
