from typing import Tuple, Union, Optional, Iterable

from . import SlotBase, Entity


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


class DocToken(SlotBase):

    __slots__ = ("doc", "token", "offset")

    def __init__(self, *, doc: "Doc", token: Token, offset: int):
        self.doc = doc
        self.token = token
        self.offset = offset

    def __str__(self):
        return self.token

    def __repr__(self):
        return f"{self.token} [offset: {self.offset}]"

    def __lt__(self, other):
        return self.offset < other.offset

    def dict(self, **_):
        return dict(offset=self.offset, token=self.token)


class HasTokens(SlotBase):

    __slots__ = ("text", "tokens")

    def __init__(
        self, *, text: str, tokens: Iterable[DocToken] = None, doc=None
    ):
        self.text = text

        if tokens:
            tokens = [
                DocToken(doc=doc, **token)
                if isinstance(token, dict)
                else token
                for token in tokens
            ]

        tokens = tupilify(tokens)

        self.tokens = tokens

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


class DocEntity(HasTokens):
    __slots__ = (
        "text",
        "tokens",
        "doc",
        "entity",
        "entity_key",
        "_sort_order",
    )

    def __init__(
        self,
        *,
        text: str,
        doc: "Doc",
        entity_key: str = None,
        entity: Optional["EntityValue"] = None,
        tokens: Iterable[DocToken] = None,
    ):
        super().__init__(text=text, tokens=tokens, doc=doc)

        self.doc = doc
        self.entity = Entity.create(entity)
        self.entity_key = entity_key or self.entity.key
        self._sort_order = None

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
        if self._sort_order is None:
            self._sort_order = (
                -self.num_tokens,
                0 if self.is_match_exact else 1,
                0 if self.is_lower_match else 1,
                # 0 if self.is_synonym_exact else 1,
                self.offset,
                self.label,
            )
        return self._sort_order

    def dict(self, **_):
        return dict(
            text=self.text,
            entity_key=self.entity_key,
            entity=self.entity.dict() if self.entity else None,
            tokens=[t.dict() for t in self.tokens],
        )


class Doc(HasTokens):

    __slots__ = ("text", "tokens", "entities")

    def __init__(
        self,
        *,
        text: str,
        entities: Tuple[DocEntity] = None,
        tokens: Tuple[DocToken] = None,
    ):
        super().__init__(text=text, tokens=tokens, doc=self)

        if entities:
            entities = [
                DocEntity(doc=self, **entity)
                if isinstance(entity, dict)
                else entity
                for entity in entities
            ]

        self.entities = tupilify(entities)


EntityValue = Union[Entity, dict, DocEntity, str, float]


def tupilify(values: Union[list, tuple, set]) -> tuple:
    """ Converts values to a sorted, unique tuple. """
    if values:
        values = tuple(sorted(set(values)))
    else:
        values = tuple()
    return values
