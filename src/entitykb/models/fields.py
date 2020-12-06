from typing import Tuple, TYPE_CHECKING
from entitykb import environ


class SmartList(object):
    """ List that conserves memory based on contents. """

    __slots__ = ["value", "is_list"]

    def __init__(self):
        self.value = None
        self.is_list = False

    def __len__(self):
        if self.is_list:
            return len(self.value)
        elif self.value is None:
            return 0
        else:
            return 1

    def __iter__(self):
        if self.is_list:
            yield from self.value
        elif self.value is not None:
            yield self.value

    def append(self, new_val):
        if self.is_list:
            self.value.append(new_val)
        elif self.value is None:
            self.value = new_val
        else:
            self.value = [self.value, new_val]
            self.is_list = True

    def remove(self, rem_val):
        if self.is_list:
            self.value = [v for v in self.value if v != rem_val]
            if len(self.value) == 1:
                self.value = self.value[0]
                self.is_list = False

        elif self.value == rem_val:
            self.value = None


class CustomField(object):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        raise NotImplementedError


StrTupleField = Tuple[str, ...]

if not TYPE_CHECKING:

    class StrTupleField(tuple, CustomField):
        @classmethod
        def validate(cls, v):
            if not v:
                v = ()

            elif isinstance(v, str):
                v = tuple(v.split(environ.mv_split))

            elif isinstance(v, list):
                v = tuple(v)

            return v
