import re
import enum

from .funcs import ensure_iterable


@enum.unique
class Direction(str, enum.Enum):
    outgoing = "outgoing"
    incoming = "incoming"

    @property
    def is_outgoing(self):
        return Direction.outgoing == self

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
    contains = "contains"
    exact = "exact"
    gt = "gt"
    gte = "gte"
    icontains = "icontains"
    iexact = "iexact"
    is_in = "is_in"
    lt = "lt"
    lte = "lte"
    not_equal = "not_equal"
    startswith = "startswith"
    istartswith = "istartswith"
    endswith = "endswith"
    iendswith = "iendswith"
    range = "range"
    regex = "regex"
    iregex = "iregex"

    @property
    def eval(self):
        method_name = f"do_{self.name}"
        method_func = getattr(self, method_name)
        return method_func

    @classmethod
    def do_exact(cls, compare_value, field_value):
        return field_value == compare_value

    @classmethod
    def do_iexact(cls, compare_value, field_value):
        return field_value.lower() == compare_value.lower()

    @classmethod
    def do_gte(cls, compare_value, field_value):
        return field_value >= compare_value

    @classmethod
    def do_gt(cls, compare_value, field_value):
        return field_value > compare_value

    @classmethod
    def do_lte(cls, compare_value, field_value):
        return field_value <= compare_value

    @classmethod
    def do_lt(cls, compare_value, field_value):
        return field_value < compare_value

    @classmethod
    def do_not_equal(cls, compare_value, field_value):
        return field_value != compare_value

    @classmethod
    def do_is_in(cls, compare_value, field_value):
        return field_value in compare_value

    @classmethod
    def do_contains(cls, compare_value, field_value):
        return compare_value in field_value

    @classmethod
    def do_icontains(cls, compare_value: str, field_value: str):
        return str(compare_value).lower() in str(field_value).lower()

    @classmethod
    def do_startswith(cls, compare_value: str, field_value: str):
        return str(field_value).startswith(str(compare_value))

    @classmethod
    def do_istartswith(cls, compare_value: str, field_value: str):
        return str(field_value).lower().startswith(str(compare_value).lower())

    @classmethod
    def do_endswith(cls, compare_value: str, field_value: str):
        return str(field_value).endswith(str(compare_value))

    @classmethod
    def do_iendswith(cls, compare_value: str, field_value: str):
        return str(field_value).lower().endswith(str(compare_value).lower())

    @classmethod
    def do_range(cls, compare_value, field_value):
        start, end = compare_value
        return start <= field_value <= end

    @classmethod
    def do_regex(cls, compare_value: str, field_value: str):
        pattern = re.compile(compare_value)
        return pattern.match(str(field_value)) is not None

    @classmethod
    def do_iregex(cls, compare_value: str, field_value: str):
        pattern = re.compile(compare_value, re.IGNORECASE)
        return pattern.match(str(field_value)) is not None


@enum.unique
class TripleSep(str, enum.Enum):
    sve = "\1"  # start -> verb -> end -> json
    vse = "\2"  # verb -> start -> end
    evs = "\3"  # end -> verb -> start
    vbs = "\4"  # verb

    @property
    def is_sve(self):
        return self == TripleSep.sve

    @property
    def is_vse(self):
        return self == TripleSep.vse


@enum.unique
class UserStatus(str, enum.Enum):
    invalid = "invalid"
    inactive = "inactive"
    read_only = "read_only"
    read_write = "read_write"

    @property
    def can_read(self):
        return self != UserStatus.inactive

    @property
    def can_write(self):
        return self == UserStatus.read_write
