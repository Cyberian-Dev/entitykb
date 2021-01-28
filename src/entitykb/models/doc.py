from __future__ import annotations
import enum

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


class SpanMatch(int, enum.Enum):
    ExactName = 0
    ExactSynonym = 1
    LowercaseName = 2
    LowercaseSynonym = 2


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
        return (self.entity and self.entity.name) or ""

    @property
    def label(self):
        return (self.entity and self.entity.label) or "ENTITY"

    @property
    def synonyms(self):
        return (self.entity and self.entity.synonyms) or []

    def match_type(self) -> SpanMatch:
        """ Lower score indicates closer match. """
        if self.text == self.name:
            match = SpanMatch.ExactName
        elif self.text in self.synonyms:
            match = SpanMatch.ExactSynonym
        elif self.text.lower() == self.name.lower():
            match = SpanMatch.LowercaseName
        else:
            match = SpanMatch.LowercaseSynonym
        return match


class Doc(HasTokens):
    text: str
    spans: Tuple[Span, ...] = None
    tokens: Tuple[DocToken, ...] = None

    @property
    def entities(self):
        return tuple(span.entity for span in self.spans if span.entity)


class ParseRequest(BaseModel):
    text: str
    labels: Optional[List[str]] = None
    pipeline: str = "default"
