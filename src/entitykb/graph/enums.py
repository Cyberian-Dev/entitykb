import enum

from .funcs import ensure_iterable


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
