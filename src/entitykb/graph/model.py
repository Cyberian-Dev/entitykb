import functools
from importlib import import_module
import enum

from typing import Tuple, Union
from uuid import uuid4


class Direction(str, enum.Enum):
    outgoing = "outgoing"
    incoming = "incoming"

    @classmethod
    def as_tuple(cls, directions, all_if_none=False):
        values = tuple()
        directions = ensure_iterable(directions or ())

        for d in directions:
            if isinstance(d, str):
                d = Direction[d]
            values = values + (d,)

        if all_if_none and not values:
            values = (Direction.outgoing, Direction.incoming)

        return values


class Base(object):
    """ Each subclass must define __slots__ """

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(repr(self))

    @property
    def _klass(self):
        return f"{self.__module__}.{self.__class__.__name__}"

    def dict(self):
        data = dict(_klass=self._klass)

        for name in self.__slots__:
            value = getattr(self, name)
            value = self._convert(value)
            data[name] = value

        return data

    @classmethod
    def _convert(cls, value):
        if isinstance(value, Base):
            return value.dict()

        if isinstance(value, (tuple, list, set)):
            return tuple([cls._convert(v) for v in value])

        if isinstance(value, enum.Enum):
            return value.value

        return value

    @classmethod
    def create(cls, _item=None, **kwargs):
        if _item is None and len(kwargs) == 0:
            return None

        if isinstance(_item, Base):
            return _item

        if isinstance(_item, dict):
            kwargs = {**_item, **kwargs}

        klass = kwargs.pop("_klass", None)
        if isinstance(klass, str):
            klass = get_class_from_name(klass)
        klass = klass or cls

        return klass(**kwargs)


class Node(Base):

    __slots__ = ["key", "label", "meta"]

    def __init__(
        self, *, key: str = None, label: str = None, meta: dict = None, **kw
    ):
        self.key = key or str(uuid4())
        self.label = label
        self.meta = {**(meta or {}), **kw}

    def __rshift__(self, tag):
        return Edge(start=self.key, tag=tag, end=None)

    def __repr__(self):
        return f"Node(key='{self.key}')"

    @staticmethod
    def to_key(node_key: Union["Node", str]) -> str:
        return node_key.key if isinstance(node_key, Node) else node_key


class Entity(Node):

    __slots__ = ["key", "label", "meta", "name", "synonyms"]

    def __init__(
        self,
        *,
        name: str,
        label: str = None,
        synonyms: Tuple[str] = None,
        key: str = None,
        meta: dict = None,
        **kw,
    ):
        self.name = name
        self.synonyms = tuple(synonyms or ())

        label = label or "ENTITY"
        key = key or f"{name}|{label}"

        super().__init__(key=key, label=label, meta=meta, **kw)

    def __repr__(self):
        return f"Entity(name='{self.name}', label='{self.label}')"

    @property
    def terms(self):
        return (self.name,) + (self.synonyms or ())


class Edge(Base):

    __slots__ = ["start", "tag", "end", "weight", "meta"]

    def __init__(
        self,
        *,
        start: str,
        tag: str,
        end: str,
        weight: int = 1,
        meta: dict = None,
        **kw,
    ):
        self.start = Node.to_key(start)
        self.tag = tag
        self.end = Node.to_key(end)
        self.weight = weight
        self.meta = {**(meta or {}), **kw}

    def __repr__(self):
        return (
            f"Edge(start='{self.start}', tag='{self.tag}', end='{self.end}')"
        )

    def __rshift__(self, end: Union[Node, str]):
        self.end = Node.to_key(end)
        return self


class Filter(Base):

    __slots__ = ["keys", "labels", "tags", "directions", "self_ok"]

    def __init__(
        self,
        *,
        keys=None,
        labels=None,
        tags=None,
        directions=None,
        self_ok=False,
    ):
        self.keys = set(ensure_iterable(keys or ()))
        self.labels = set(ensure_iterable(labels or ()))
        self.tags = set(ensure_iterable(tags or ()))
        self.directions = Direction.as_tuple(directions, all_if_none=True)
        self.self_ok = self_ok


class Step(Base):
    pass


class WalkStep(Step):

    __slots__ = ["tags", "directions", "max_hops", "passthru"]

    def __init__(
        self,
        tags=None,
        directions=Direction.incoming,
        max_hops=None,
        passthru=False,
    ):
        self.tags = ensure_iterable(tags or (), f=set)
        self.directions = Direction.as_tuple(directions, all_if_none=True)
        self.max_hops = max_hops
        self.passthru = passthru


class FilterStep(Step):

    __slots__ = ["filters", "join_type", "exclude"]

    def __init__(self, *, filters=None, join_type="AND", exclude=False):
        self.filters = [Filter.create(f) for f in ensure_iterable(filters)]
        self.join_type = join_type
        self.exclude = exclude


class Query(Base):

    __slots__ = ["initial", "steps", "limit", "offset"]

    def __init__(
        self,
        initial: tuple = None,
        steps: tuple = None,
        limit: int = None,
        offset: int = 0,
    ):
        self.initial = tuple(
            Node.to_key(node) for node in ensure_iterable(initial or ())
        )
        self.steps = tuple(
            [Step.create(step) for step in ensure_iterable(steps or ())]
        )
        self.limit = limit
        self.offset = offset


@functools.lru_cache(maxsize=100)
def get_class_from_name(full_name: str):
    module_name, class_name = full_name.rsplit(".", 1)
    module = import_module(module_name)
    klass = getattr(module, class_name)
    return klass


def is_iterable(items):
    return isinstance(items, (list, set, dict, frozenset, tuple))


def ensure_iterable(items, f=tuple, explode_first=False):
    if not is_iterable(items):
        items = f((items,))

    elif explode_first and len(items) == 1:
        first_item = next(iter(items))
        if is_iterable(first_item):
            items = f(first_item)

    return items
