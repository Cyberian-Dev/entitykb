from typing import Tuple, Union, Optional, Set, Iterable

from .utils import get_class_from_name, tupilify


class BaseModel(object):
    def __eq__(self, other):
        return hash(self) == hash(other)


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


class Correction(BaseModel):
    def __init__(self, *, distance: int, ratio: int):
        self.distance = distance
        self.ratio = ratio

    def __str__(self):
        return f"<Correction: ratio={self.ratio} / dist={self.distance}"

    def dict(self):
        return dict(distance=self.distance, ratio=self.ratio,)

    @classmethod
    def convert(cls, value: Union[dict, "Correction"]):
        if isinstance(value, dict):
            value = cls(**value)
        return value


class Entity(BaseModel):

    __slots__ = ("name", "key", "label", "synonyms", "meta")

    def __init__(
        self,
        *,
        name: str,
        key: str = None,
        label: str = None,
        synonyms: Tuple[str, ...] = None,
        meta: dict = None,
    ):
        self.name = name
        self.label = label or self.__class__.__name__.upper()
        self.key = key or f"{self.name}|{self.label}"
        self.synonyms = tupilify(synonyms)
        self.meta = meta

    def __repr__(self):
        return self.key

    def __hash__(self):
        return hash(("Entity", self.key))

    @property
    def terms(self):
        yield self.name
        for synonym in self.synonyms or []:
            yield synonym

    def dict(self) -> dict:
        return dict(
            name=self.name,
            key=self.key,
            label=self.label,
            synonyms=self.synonyms,
            meta=self.meta,
        )

    @classmethod
    def convert(cls, value: "EntityValue"):
        if isinstance(value, dict):
            value = cls.from_dict(value)
        elif isinstance(value, Entity) and not isinstance(value, cls):
            value = cls(**value.dict())
        return value

    @classmethod
    def field_names(cls):
        return {"name", "label", "key", "synonyms"}

    @classmethod
    def copy_and_clean(cls, record: dict, mv_keys: Set[str], mv_sep: str):
        copy = {}

        for key, value in record.items():
            if value is None:
                continue

            value = value.strip() if isinstance(value, str) else value
            if key in mv_keys:
                value = list(filter(None, value.split(mv_sep)))

            copy[key] = value

        return copy

    @classmethod
    def from_dict(
        cls,
        record: dict,
        mv_keys: Set[str] = None,
        mv_sep: str = None,
        key_format: str = "{name}|{label}",
        ignore: list = None,
    ):
        mv_keys = mv_keys or set()
        mv_sep = mv_sep or "|"

        meta_values = cls.copy_and_clean(record, mv_keys, mv_sep)

        class_name = meta_values.pop("class_name", None)
        klass = get_class_from_name(class_name) if class_name else cls
        field_names = klass.field_names()

        field_values = {}
        for field_name in field_names:
            field_values[field_name] = meta_values.pop(field_name, None)

        for ignore_name in ignore or []:
            meta_values.pop(ignore_name, None)

        if meta_values:
            field_values["meta"] = meta_values

        if not field_values.get("label"):
            field_values["label"] = cls.__name__.upper()

        if not field_values.get("key"):
            field_values["key"] = key_format.format(**field_values)

        return klass(**field_values)


class DocToken(BaseModel):

    __slots__ = ("doc", "token", "offset")

    def __init__(self, *, doc: "Doc", token: Token, offset: int):
        self.doc = doc
        self.token = token
        self.offset = offset

    def __str__(self):
        return self.token

    def __repr__(self):
        return f"{self.token} [offset: {self.offset}]"

    def __hash__(self):
        return hash(("DocToken", self.offset, self.token, id(self.doc)))

    def __lt__(self, other):
        return self.offset < other.offset

    def dict(self, **_):
        return dict(offset=self.offset, token=self.token)


class HasTokens(BaseModel):

    __slots__ = ("text", "tokens")

    def __init__(self, *, text: str, tokens: Iterable[DocToken] = None):
        self.text = text

        if tokens:
            tokens = [
                DocToken(**token) if isinstance(token, dict) else token
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

    def __lt__(self, other: "HasTokens"):
        return self.tokens < other.tokens

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

    def dict(self, **_):
        return dict(text=self.text, tokens=[t.dict() for t in self.tokens])


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
        correction: Correction = None,
        tokens: Iterable[DocToken] = None,
    ):
        super().__init__(text=text, tokens=tokens)

        self.doc = doc
        self.entity = Entity.convert(entity)
        self.entity_key = entity_key or repr(self.entity)
        self.correction = Correction.convert(correction)
        self._sort_order = None

    def __str__(self):
        return f"{self.text} [{self.entity_key}]"

    def __hash__(self):
        return hash(("DocEntity", self.entity_key, self.offsets, id(self.doc)))

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
    def has_correction(self):
        return self.correction is not None

    @property
    def distance(self):
        return self.correction.distance if self.correction else 0

    @property
    def ratio(self):
        return self.correction.ratio if self.correction else 100

    @property
    def meta(self):
        if self.entity:
            return self.entity.meta

    @property
    def sort_order(self):
        if self._sort_order is None:
            self._sort_order = (
                -self.num_tokens,
                self.has_correction,
                -self.ratio,
                self.distance,
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
            correction=self.correction.dict() if self.correction else None,
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
        super().__init__(text=text, tokens=tokens)
        self.entities = tupilify(entities)

    def __hash__(self):
        return hash(
            ("Doc", self.text, tuple(self.tokens), tuple(self.entities))
        )

    def dict(self):
        return dict(
            text=self.text,
            entities=[entity.dict() for entity in self.entities],
            tokens=[token.dict() for token in self.tokens],
        )


class FindResult(BaseModel):

    __slots__ = ("term", "entities", "distance")

    def __init__(
        self, term: str, entities=None, distance=None,
    ):
        self.term = term
        self.entities = entities or tuple()
        self.distance = distance

    def __hash__(self):
        return hash(("FindResult", self.term, self.entity_keys))

    def __str__(self):
        return f"{self.term} [{','.join(self.entity_keys)}]"

    def __repr__(self):
        return f"{self.term} [{','.join(self.entity_keys)}]"

    def __len__(self):
        return len(self.entities)

    def __bool__(self):
        return len(self.entities) > 0

    def __iter__(self):
        for entity in self.entities:
            yield entity.key, entity

    @property
    def entity_keys(self):
        return tuple(entity.key for entity in self.entities)


class LabelSet(object):

    __slots__ = ("allow_any", "labels")

    def __init__(self, *args, **kwargs):
        self.allow_any = kwargs.pop("allow_any", None)
        self.labels = kwargs.pop("labels", None) or []

        for arg in args:
            if isinstance(arg, bool):
                self.allow_any = arg
            elif isinstance(arg, Iterable):
                self.labels += list(arg)
            elif arg is None:
                self.allow_any = True
            else:
                self.labels.add(arg)

        self.labels = set(self.labels)

        if self.allow_any is None:
            self.allow_any = len(self.labels) == 0

    def __repr__(self):
        if self.allow_any:
            msg = "Allow Any"
        elif self.labels:
            msg = ", ".join(self.labels)
        else:
            msg = "No Labels Allowed"
        return f"<LabelSet: {msg}>"

    def __contains__(self, item):
        return item in self.labels

    def add_label(self, label):
        if label not in self.labels:
            self.labels.add(label)

    def intersect(self, item) -> "LabelSet":
        if item is None:
            return self

        else:
            other = LabelSet.create(item)

            if other.allow_any:
                return self

            elif self.allow_any:
                return other

            else:
                common = self.labels.intersection(other.labels)
                if common:
                    return LabelSet(labels=common)

    def is_allowed(self, item):
        if self.allow_any:
            return True

        return self.intersect(item) is not None

    def dict(self) -> dict:
        return {"allow_any": self.allow_any, "labels": sorted(self.labels)}

    @classmethod
    def create(cls, item=None) -> "LabelSet":  # pragma: no mccabe
        if isinstance(item, LabelSet):
            return item

        kwargs = {}
        if item is None:
            kwargs["allow_any"] = True
        elif isinstance(item, dict):
            kwargs = item
        elif isinstance(item, bool):
            kwargs["allow_any"] = item
        elif isinstance(item, (Entity, DocEntity)):
            kwargs["labels"] = [item.label]
        elif isinstance(item, str):
            kwargs["labels"] = [item]
        elif isinstance(item, Iterable):
            kwargs["labels"] = item

        return LabelSet(**kwargs)


EntityValue = Union[Entity, dict]
