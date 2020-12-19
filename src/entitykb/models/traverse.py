from typing import Any, List, Optional

from pydantic import validator, BaseModel, Field

from .enums import Direction, Comparison
from .funcs import ensure_iterable
from .node import Node


class Criteria(BaseModel):
    type: str = None

    __mapping__ = None

    @classmethod
    def identify_class(cls, type: str, **_):
        if cls.__mapping__ is None:
            cls.__mapping__ = dict(field=FieldCriteria, edge=EdgeCriteria)
        return cls.__mapping__.get(type)

    @classmethod
    def create(cls, _item=None, **kwargs):
        if isinstance(_item, cls):
            return _item

        if isinstance(_item, dict):
            kwargs = {**_item, **kwargs}

        klass = cls.identify_class(**kwargs)
        return klass(**kwargs)


class FieldCriteria(Criteria):
    field: str
    compare: Comparison = None
    value: Any = None
    type: str = "field"

    def set(self, compare: Comparison, value):
        self.compare = compare
        self.value = value
        return self

    def do_compare(self, value) -> bool:
        return self.compare.eval(self.value, value)

    # operator-based
    # references:
    # https://docs.python.org/3/library/operator.html

    def __eq__(self, value):
        return self.exact(value)

    def __ge__(self, value):
        return self.gte(value)

    def __gt__(self, value):
        return self.gt(value)

    def __le__(self, value):
        return self.lte(value)

    def __lt__(self, value):
        return self.lt(value)

    def __ne__(self, value):
        return self.not_equal(value)

    # name methods
    # reference:
    # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#field-lookups

    def exact(self, value):
        return self.set(Comparison.exact, value)

    def iexact(self, value):
        return self.set(Comparison.iexact, value)

    def contains(self, value):
        return self.set(Comparison.contains, value)

    def icontains(self, value):
        return self.set(Comparison.icontains, value)

    def is_in(self, values):
        values = set(values)
        return self.set(Comparison.is_in, values)

    def gt(self, value):
        return self.set(Comparison.gt, value)

    def gte(self, value):
        return self.set(Comparison.gte, value)

    def lte(self, value):
        return self.set(Comparison.lte, value)

    def lt(self, value):
        return self.set(Comparison.lt, value)

    def startswith(self, value: str):
        return self.set(Comparison.startswith, value)

    def istartswith(self, value: str):
        return self.set(Comparison.istartswith, value)

    def endswith(self, value: str):
        return self.set(Comparison.endswith, value)

    def iendswith(self, value: str):
        return self.set(Comparison.iendswith, value)

    def range(self, min_val, max_val):
        return self.set(Comparison.range, (min_val, max_val))

    def regex(self, value):
        return self.set(Comparison.regex, value)

    def iregex(self, value):
        return self.set(Comparison.iregex, value)

    # named methods

    def not_equal(self, value):
        return self.set(Comparison.not_equal, value)


class EdgeCriteria(Criteria):
    verbs: List[str]
    directions: List[Direction]
    keys: List[str]
    type: str = "edge"

    @validator("verbs", "directions", pre=True, always=True)
    def to_list(cls, v):
        return ensure_iterable(v, f=list)

    @validator("keys", pre=True, always=True)
    def to_key_tuple(cls, v):
        return list(Node.to_key(n) for n in ensure_iterable(v))


class Step(BaseModel):
    @classmethod
    def create(cls, _item=None, **kwargs):
        if isinstance(_item, cls):
            return _item

        if isinstance(_item, dict):
            kwargs = {**_item, **kwargs}

        if "max_hops" in kwargs.keys():
            return WalkStep(**kwargs)
        else:
            return FilterStep(**kwargs)


class WalkStep(Step):
    verbs: List[str] = None
    directions: List[Direction] = [
        Direction.incoming,
    ]
    max_hops: Optional[int] = 1
    passthru: bool = False

    @validator("verbs", pre=True, always=True)
    def ensure_verbs(cls, v):
        return [Verb(t) for t in ensure_iterable(v or ())]

    @validator("directions", pre=True, always=True)
    def ensure_directions(cls, v):
        return list(ensure_iterable(v or ()))


class FilterStep(Step):
    criteria: List[Any] = []
    all: bool = False
    exclude: bool = False

    @validator("criteria", pre=True, always=True)
    def ensure_criteria(cls, v):
        return [Criteria.create(c) for c in ensure_iterable(v or ())]


# noinspection PyShadowingBuiltins
class Traversal(BaseModel):
    __root__: List[Step] = Field(default_factory=list)

    def __init__(self, **kwargs):
        steps = kwargs.get("__root__", [])
        steps = [Step.create(s) for s in steps]
        super().__init__(__root__=steps)

    def __len__(self):
        return len(self.__root__)

    def append(self, item):
        return self.__root__.append(item)

    def __getitem__(self, item):
        return self.__root__[item]

    def __iter__(self):
        return iter(self.__root__)

    def copy(self, **_):
        return Traversal(__root__=self.__root__)

    def dict(self, *args, **kwargs):
        return [step.dict() for step in self.__root__]

    # walk nodes

    def all_nodes(
        self, *verbs: str, max_hops: int = 1, passthru: bool = False
    ):
        return self._walk_nodes(
            *verbs,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.outgoing, Direction.incoming),
        )

    def out_nodes(
        self, *verbs: str, max_hops: int = 1, passthru: bool = False
    ):
        return self._walk_nodes(
            *verbs,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.outgoing,),
        )

    def in_nodes(self, *verbs: str, max_hops: int = 1, passthru: bool = False):
        return self._walk_nodes(
            *verbs,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.incoming,),
        )

    # filter

    def include(self, *criteria, all=False):
        return self._add_filter(*criteria, all=all, exclude=False)

    def exclude(self, *criteria, all=False):
        return self._add_filter(*criteria, all=all, exclude=True)

    # private functions

    def _add_filter(
        self, *criteria: Criteria, all: bool = False, exclude: bool = False
    ):
        step = FilterStep(criteria=list(criteria), all=all, exclude=exclude)
        self.append(step)
        return self

    def _walk_nodes(
        self,
        *verbs: str,
        max_hops: int = None,
        passthru: bool = False,
        directions=None,
    ):
        walk = WalkStep(
            verbs=list(verbs),
            directions=Direction.as_tuple(directions, all_if_none=True),
            max_hops=max_hops,
            passthru=passthru,
        )
        self.append(walk)
        return self


T = Traversal


class FieldCriteriaBuilderType(type):
    def __getattr__(self, field: str):
        return FieldCriteria(field=field)


class FieldCriteriaBuilder(object, metaclass=FieldCriteriaBuilderType):
    pass


F = FieldCriteriaBuilder


class VerbType(type):
    cache = {}

    def __getattr__(self, verb_name: str):
        try:
            return Verb.cache[verb_name]
        except KeyError:
            upper_case = verb_name.upper()

            try:
                verb = Verb.cache[upper_case]
            except KeyError:
                verb = Verb(upper_case)

            Verb.cache[verb_name] = verb
            Verb.cache[upper_case] = verb
            return verb


class Verb(str, metaclass=VerbType):
    def __call__(self, item):
        return Verb.__getattr__(item)

    def __rshift__(self, nodes):
        return EdgeCriteria(
            verbs=[self], directions=[Direction.outgoing], keys=nodes
        )

    def __lshift__(self, nodes):
        return EdgeCriteria(
            verbs=[self], directions=[Direction.incoming], keys=nodes
        )

    def __pow__(self, nodes):
        return EdgeCriteria(
            verbs=[self],
            directions=[Direction.incoming, Direction.outgoing],
            keys=nodes,
        )


V = Verb
