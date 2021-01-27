from typing import Tuple, TYPE_CHECKING


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
                v = tuple(v.split("|"))

            elif isinstance(v, list):
                v = tuple(v)

            return v
