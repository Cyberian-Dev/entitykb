import enum
from typing import Tuple, Union, Iterable
from uuid import uuid4

from entitykb.funcs import ensure_iterable
from .enums import Direction, Comparison


class SlotBase(object):
    """ Each subclass must define __slots__ """

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        data = self.dict()
        items = sorted(f"{k}={v}" for k, v in data.items() if v is not None)
        return f"<{self.__class__.__name__}: {', '.join(items)}>"

    def dict(self):
        data = dict()

        for name in self.__slots__:
            value = getattr(self, name)
            value = self._convert(value)
            data[name] = value

        return data

    @classmethod
    def _convert(cls, value):
        if isinstance(value, SlotBase):
            return value.dict()

        if isinstance(value, (tuple, list, set)):
            return tuple([cls._convert(v) for v in value])

        if isinstance(value, enum.Enum):
            return value.value

        return value

    @classmethod
    def get_subclass(cls, keys):
        pass

    @classmethod
    def create(cls, _item=None, *, _klass=None, **kwargs):
        if _item is None and len(kwargs) == 0:
            return None

        if isinstance(_item, cls):
            return _item

        if isinstance(_item, dict):
            kwargs = {**_item, **kwargs}

        _klass = _klass or cls.get_subclass(keys=kwargs.keys())
        _klass = _klass or cls

        return _klass(**kwargs)


class Criteria(SlotBase):
    @classmethod
    def get_subclass(cls, keys):
        if keys == set(AttrCriteria.__slots__):
            return AttrCriteria
        else:
            return RelCriteria


class AttrCriteriaType(type):
    def __getattr__(self, attr_name: str):
        return AttrCriteria(attr_name)


class AttrCriteria(Criteria, metaclass=AttrCriteriaType):

    __slots__ = ["attr_name", "compare", "value"]

    def __init__(
        self, attr_name: str, compare: Comparison = None, value=None,
    ):
        self.attr_name = attr_name
        self.compare = compare
        self.value = value

    def set(self, compare: Comparison, value):
        self.compare = compare
        self.value = value
        return self

    def __eq__(self, other):
        return self.set(Comparison.eq, other)

    def __ge__(self, other):
        return self.set(Comparison.ge, other)

    def __gt__(self, other):
        return self.set(Comparison.gt, other)

    def __le__(self, other):
        return self.set(Comparison.le, other)

    def __lt__(self, other):
        return self.set(Comparison.lt, other)

    def __ne__(self, other):
        return self.set(Comparison.ne, other)

    def do_compare(self, other) -> bool:
        method_name = f"do_{self.compare.name}"
        method_func = getattr(self, method_name)
        result = method_func(other)
        return result

    def do_eq(self, other):
        return other == self.value

    def do_ge(self, other):
        return other >= self.value

    def do_gt(self, other):
        return other > self.value

    def do_le(self, other):
        return other <= self.value

    def do_lt(self, other):
        return other < self.value

    def do_ne(self, other):
        return other != self.value


class RelCriteriaType(type):
    def __getattr__(self, tag: str):
        tag = tag.upper()
        return RelCriteria(tag)


class RelCriteria(Criteria, metaclass=RelCriteriaType):

    __slots__ = ["tags", "nodes", "directions"]

    def __init__(self, tags: str, directions=None, nodes=None):
        self.tags = ensure_iterable(tags)
        self.directions = ensure_iterable(directions)
        self.nodes = Node.to_key_tuple(nodes)

    def __rshift__(self, nodes):
        self.directions = (Direction.outgoing,)
        self.nodes = Node.to_key_tuple(nodes)
        return self

    def __lshift__(self, nodes):
        self.directions = (Direction.incoming,)
        self.nodes = Node.to_key_tuple(nodes)
        return self

    def __pow__(self, nodes):
        self.directions = (Direction.incoming, Direction.outgoing)
        self.nodes = Node.to_key_tuple(nodes)
        return self


class Node(SlotBase):

    __slots__ = ["key", "label", "attrs"]

    def __init__(
        self, *, key: str = None, label: str = None, attrs: dict = None, **kw
    ):
        self.key = key or str(uuid4())
        self.label = label
        self.attrs = {**(attrs or {}), **kw}

    def __rshift__(self, tag):
        return Edge(start=self.key, tag=tag, end=None)

    def __lshift__(self, tag):
        return Edge(start=None, tag=tag, end=self.key)

    def __repr__(self):
        return f"<Node: key={self.key} attrs={self.attrs}>"

    def __getattr__(self, item):
        if item == "attrs":
            raise AttributeError

        if item in self.attrs:
            return self.attrs.get(item)
        else:
            raise AttributeError

    @staticmethod
    def to_key(node_key: Union["Node", str]) -> str:
        return node_key.key if isinstance(node_key, Node) else node_key

    @staticmethod
    def to_key_tuple(nodes):
        return tuple(Node.to_key(n) for n in ensure_iterable(nodes))

    @property
    def terms(self):
        return ()


class Entity(Node):

    __slots__ = ["key", "label", "attrs", "name", "synonyms"]

    def __init__(
        self,
        *,
        name: str,
        label: str = None,
        synonyms: Tuple[str] = None,
        key: str = None,
        attrs: dict = None,
        **kw,
    ):
        self.name = name
        self.synonyms = tuple(synonyms or ())

        label = label or "ENTITY"
        key = key or f"{name}|{label}"

        super().__init__(key=key, label=label, attrs=attrs, **kw)

    def __repr__(self):
        return "<Entity: " f"name={self.name}, label={self.label}>"

    @property
    def terms(self):
        return (self.name,) + (self.synonyms or ())


class Edge(SlotBase):

    __slots__ = ["start", "tag", "end", "weight", "attrs"]

    def __init__(
        self,
        *,
        start: str,
        tag: str,
        end: str,
        weight: int = 1,
        attrs: dict = None,
        **kw,
    ):
        self.start = Node.to_key(start)
        self.tag = tag.upper()
        self.end = Node.to_key(end)
        self.weight = weight
        self.attrs = {**(attrs or {}), **kw}

    def __repr__(self):
        return (
            "<entitykb.graph.model.Edge: "
            f"start={self.start}, tag={self.tag}, end={self.end}>"
        )

    def __rshift__(self, end: Union[Node, str]):
        self.end = Node.to_key(end)
        return self

    def __lshift__(self, start: Union[Node, str]):
        self.start = Node.to_key(start)
        return self


class Step(SlotBase):
    @classmethod
    def get_subclass(cls, keys):
        if keys == set(WalkStep.__slots__):
            return WalkStep
        else:
            return FilterStep


class WalkStep(Step):

    __slots__ = ["tags", "directions", "max_hops", "passthru"]

    def __init__(
        self,
        tags=None,
        directions=Direction.incoming,
        max_hops=1,
        passthru=False,
    ):
        self.tags = tuple(t.upper() for t in ensure_iterable(tags or ()))
        self.directions = Direction.as_tuple(directions, all_if_none=True)
        self.max_hops = max_hops
        self.passthru = passthru

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return hash(self) == hash(other)


class FilterStep(Step):

    __slots__ = ["criteria", "all", "exclude"]

    def __init__(self, *, criteria=None, all=False, exclude=False):
        criteria = ensure_iterable(criteria, explode_first=True)
        self.criteria = [Criteria.create(c) for c in criteria]
        self.all = all
        self.exclude = exclude


class Query(SlotBase):

    __slots__ = ["steps", "limit", "offset"]

    def __init__(
        self, steps: Iterable = None, limit: int = None, offset: int = 0,
    ):
        self.steps = [Step.create(s) for s in ensure_iterable(steps or ())]
        self.limit = limit
        self.offset = offset

    def __len__(self):
        return len(self.steps)

    def __getitem__(self, item):
        return self.steps[item]
