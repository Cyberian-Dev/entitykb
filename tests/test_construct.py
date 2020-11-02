from pydantic import BaseModel
from entitykb import create_component


class A(BaseModel):
    c: int = None


class B(A):
    pass


def test_create_component():
    obj = create_component(None, A, B, c=1)
    assert isinstance(obj, B)
    assert obj.c == 1

    obj = create_component(B(), A, B, c=2)
    assert isinstance(obj, B)
    assert obj.c == 2
