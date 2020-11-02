from typing import Any, List, Optional

from pydantic import validator, BaseModel

from . import ensure_iterable, Direction, Comparison, Node, chain


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
    attr_name: str
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
        return self.set(Comparison.exact, value)

    def __ge__(self, value):
        return self.set(Comparison.gte, value)

    def __gt__(self, value):
        return self.set(Comparison.gt, value)

    def __le__(self, value):
        return self.set(Comparison.lte, value)

    def __lt__(self, value):
        return self.set(Comparison.lt, value)

    def __ne__(self, value):
        return self.set(Comparison.not_equal, value)

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

    def is_in(self, *args):
        value = set(chain(args))
        return self.set(Comparison.is_in, value)

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

    def range(self, *args):
        value = tuple(chain(args))
        assert len(value), f"Range requires exactly 2 values. {value}"
        return self.set(Comparison.range, value)

    def regex(self, value):
        return self.set(Comparison.regex, value)

    def iregex(self, value):
        return self.set(Comparison.iregex, value)

    # named methods

    def not_equal(self, value):
        return self.set(Comparison.not_equal, value)


class EdgeCriteria(Criteria):
    tags: List[str]
    directions: List[Direction]
    nodes: List[str]
    type: str = "edge"

    @validator("tags", "directions", pre=True, always=True)
    def to_list(cls, v):
        return ensure_iterable(v, f=list)

    @validator("nodes", pre=True, always=True)
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
    tags: List[str] = None
    directions: List[Direction] = [
        Direction.incoming,
    ]
    max_hops: Optional[int] = 1
    passthru: bool = False

    @validator("tags", pre=True, always=True)
    def ensure_tags(cls, v):
        return [Tag(t) for t in ensure_iterable(v or ())]

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


class Query(BaseModel):
    steps: List[Step] = []
    limit: int = None
    offset: int = 0

    @validator("steps", pre=True, always=True)
    def ensure_steps(cls, v):
        return [Step.create(s) for s in ensure_iterable(v or ())]

    def __len__(self):
        return len(self.steps)

    def __getitem__(self, item):
        return self.steps[item]


class QueryBuilder(object):
    def __init__(self):
        self.query = Query()

    # walk nodes

    def all_nodes(self, *tags: str, max_hops: int = 1, passthru: bool = False):
        return self._walk_nodes(
            *tags,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.outgoing, Direction.incoming),
        )

    def out_nodes(self, *tags: str, max_hops: int = 1, passthru: bool = False):
        return self._walk_nodes(
            *tags,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.outgoing,),
        )

    def in_nodes(self, *tags: str, max_hops: int = 1, passthru: bool = False):
        return self._walk_nodes(
            *tags,
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
        filter = FilterStep(criteria=criteria, all=all, exclude=exclude)
        self.query.steps.append(filter)
        return self

    def _walk_nodes(
        self,
        *tags: str,
        max_hops: int = None,
        passthru: bool = False,
        directions=None,
    ):
        walk = WalkStep(
            tags=tags,
            directions=Direction.as_tuple(directions, all_if_none=True),
            max_hops=max_hops,
            passthru=passthru,
        )
        self.query.steps.append(walk)
        return self

    # limit (and offset)

    def all(self):
        self.query.limit = None
        return self.query

    def limit(self, limit: int):
        self.query.limit = limit
        return self.query

    def first(self):
        self.query.limit = 1
        return self.query

    def page(self, number: int = 0, size: int = 20):
        offset = number * size
        self.query.offset = offset
        self.query.limit = size
        return self.query


QB = QueryBuilder


class FieldCriteriaBuilderType(type):
    def __getattr__(self, attr_name: str):
        return FieldCriteria(attr_name=attr_name)


class FieldCriteriaBuilder(object, metaclass=FieldCriteriaBuilderType):
    pass


F = FieldCriteriaBuilder


class TagType(type):
    def __getattr__(self, tag_name: str):
        return Tag(tag_name)


class Tag(str, metaclass=TagType):
    def __new__(cls, string):
        string = string.upper()
        obj = super(Tag, cls).__new__(cls, string)
        return obj

    def __rshift__(self, nodes):
        return EdgeCriteria(
            tags=(self,), directions=(Direction.outgoing,), nodes=nodes
        )

    def __lshift__(self, nodes):
        return EdgeCriteria(
            tags=(self,), directions=(Direction.incoming,), nodes=nodes
        )

    def __pow__(self, nodes):
        return EdgeCriteria(
            tags=(self,),
            directions=(Direction.incoming, Direction.outgoing),
            nodes=nodes,
        )
