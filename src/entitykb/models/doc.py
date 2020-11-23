from __future__ import annotations

from typing import Tuple, Optional, Any, List

from pydantic import BaseModel

from .entity import Entity


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


class Span(HasTokens):
    entity_key: str
    tokens: Tuple[DocToken, ...]
    entity: Entity = None

    def __init__(self, **data: Any):
        entity = Entity.create(data.pop("entity"))

        # populate entity_key if not provided
        data.setdefault("entity_key", entity and entity.key)

        super().__init__(**data)

        # store after init to prevent stripping of subclass-specific attributes
        self.entity = entity

    def __str__(self):
        return f"{self.text} [{self.entity_key}]"

    @property
    def name(self):
        return self.entity and self.entity.name

    @property
    def label(self):
        return self.entity and (self.entity.label or "ENTITY")

    @property
    def synonyms(self):
        return (self.entity and self.entity.synonyms) or []

    @property
    def is_exact_name_match(self):
        return self.name == self.text

    @property
    def is_lower_name_match(self):
        return self.name and (self.name.lower() == self.text.lower())

    @property
    def is_lower_name_or_exact_synonym_match(self):
        return self.is_lower_name_match or (self.text in self.synonyms)


class Doc(HasTokens):
    text: str
    spans: Tuple[Span, ...] = None
    tokens: Tuple[DocToken, ...] = None

    @property
    def entities(self):
        return tuple(span.entity for span in self.spans)


class ParseRequest(BaseModel):
    text: str
    pipeline: str = "default"
    labels: List[str] = []
