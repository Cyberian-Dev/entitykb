import enum

from . import ensure_iterable


class TagType(type):
    def __getattr__(self, tag_name: str):
        return Tag(tag_name)


class Tag(str, metaclass=TagType):
    def __new__(cls, string):
        string = string.upper()
        obj = super(Tag, cls).__new__(cls, string)
        return obj

    def __rshift__(self, nodes):
        from . import RelCriteria

        return RelCriteria((self,), (Direction.outgoing,), nodes)

    def __lshift__(self, nodes):
        from . import RelCriteria

        return RelCriteria((self,), (Direction.incoming,), nodes)

    def __pow__(self, nodes):
        from . import RelCriteria

        return RelCriteria(
            (self,), (Direction.incoming, Direction.outgoing), nodes
        )


@enum.unique
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


@enum.unique
class Comparison(str, enum.Enum):
    eq = "=="
    ge = ">="
    gt = ">"
    le = "<="
    lt = "<"
    ne = "!="

    @property
    def eval(self):
        method_name = f"do_{self.name}"
        method_func = getattr(self, method_name)
        return method_func

    @classmethod
    def do_eq(cls, my_val, other_val):
        return other_val == my_val

    @classmethod
    def do_ge(cls, my_val, other_val):
        return other_val >= my_val

    @classmethod
    def do_gt(cls, my_val, other_val):
        return other_val > my_val

    @classmethod
    def do_le(cls, my_val, other_val):
        return other_val <= my_val

    @classmethod
    def do_lt(cls, my_val, other_val):
        return other_val < my_val

    @classmethod
    def do_ne(cls, my_val, other_val):
        return other_val != my_val
