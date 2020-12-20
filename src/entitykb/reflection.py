import functools
import inspect
from importlib import import_module
from typing import Callable, Iterable, Iterator, Union

istr = Union[Iterable[str], Iterator[str]]


def create_component(value, default_cls=None, **kwargs):
    component = None

    if value is None and default_cls is not None:
        component = default_cls(**kwargs)

    elif isinstance(value, str):
        component = instantiate_class_from_name(value, **kwargs)

    elif isinstance(value, inspect.getmro(default_cls)[:-1]):
        component = value
        for (k, v) in kwargs.items():
            setattr(component, k, v)

    elif isinstance(value, Callable):
        component = value(**kwargs)

    assert component is not None, f"create fail: {value}, {default_cls}"
    return component


@functools.lru_cache(maxsize=100)
def get_class_from_name(full_name: str):
    module_name, class_name = full_name.rsplit(".", 1)
    module = import_module(module_name)
    klass = getattr(module, class_name, None)
    return klass


def instantiate_class_from_name(full_name: str, *args, **kwargs):
    klass = get_class_from_name(full_name)
    if klass:
        return klass(*args, **kwargs)
