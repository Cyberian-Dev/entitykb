from typing import Iterable

from . import ensure_iterable, SlotBase, Direction, Comparison, Node


class Criteria(SlotBase):
    @classmethod
    def identify_klass(cls, kwargs):
        if kwargs.keys() == set(AttrCriteria.__slots__):
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
        return self.compare.eval(self.value, other)


class RelCriteriaType(type):
    def __getattr__(self, tag: str):
        tag = tag.upper()
        return RelCriteria(tag)


class RelCriteria(Criteria, metaclass=RelCriteriaType):

    __slots__ = ["tags", "nodes", "directions"]

    def __init__(self, tags: str, directions=None, nodes=None):
        self.tags = ensure_iterable(tags)
        self.directions = ensure_iterable(directions)
        self.nodes = RelCriteria.to_key_tuple(nodes)

    def update(self, directions, nodes):
        self.directions = ensure_iterable(directions)
        self.nodes = RelCriteria.to_key_tuple(nodes)
        return self

    def __rshift__(self, nodes):
        return self.update((Direction.outgoing,), nodes)

    def __lshift__(self, nodes):
        return self.update((Direction.incoming,), nodes)

    def __pow__(self, nodes):
        return self.update((Direction.incoming, Direction.outgoing), nodes)

    @staticmethod
    def to_key_tuple(nodes):
        return tuple(Node.to_key(n) for n in ensure_iterable(nodes))


class Step(SlotBase):
    @classmethod
    def identify_klass(cls, kwargs):
        if kwargs.keys() == set(WalkStep.__slots__):
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
