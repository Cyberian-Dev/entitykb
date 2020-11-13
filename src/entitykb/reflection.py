import functools
from importlib import import_module
from typing import Callable


def create_component(value, base_class, default_class, **kwargs):
    if value is None:
        value = default_class(**kwargs)

    elif isinstance(value, base_class):
        for (k, v) in kwargs.items():
            setattr(value, k, v)

    elif isinstance(value, str):
        value = instantiate_class_from_name(value, **kwargs)

    elif isinstance(value, Callable):
        value = value(**kwargs)

    return value


@functools.lru_cache(maxsize=100)
def get_class_from_name(full_name: str):
    module_name, class_name = full_name.rsplit(".", 1)
    module = import_module(module_name)
    klass = getattr(module, class_name)
    return klass


def instantiate_class_from_name(full_name: str, *args, **kwargs):
    klass = get_class_from_name(full_name)
    return klass(*args, **kwargs)
