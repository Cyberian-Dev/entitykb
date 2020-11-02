import functools
import re
from importlib import import_module
from typing import Iterable, Iterator
from pydantic import BaseModel

camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name, upper=False):
    name = camel_pattern.sub("_", name)
    name = name.upper() if upper else name.lower()
    return name


@functools.lru_cache(maxsize=100)
def get_class_from_name(full_name: str):
    module_name, class_name = full_name.rsplit(".", 1)
    module = import_module(module_name)
    klass = getattr(module, class_name)
    return klass


def instantiate_class_from_name(full_name: str, *args, **kwargs):
    klass = get_class_from_name(full_name)
    return klass(*args, **kwargs)


def is_iterable(items):
    return isinstance(items, (list, set, dict, frozenset, tuple))


def ensure_iterable(items, f=tuple, explode_first=False):
    if not is_iterable(items):
        items = f((items,))

    elif explode_first and len(items) == 1:
        first_item = next(iter(items))
        if is_iterable(first_item):
            items = f(first_item)

    return items


def chain(*items):
    for item in items:
        if isinstance(item, (BaseModel, str, dict)):
            yield item
        elif isinstance(item, (Iterable, Iterator)):
            yield from chain(*item)
        else:
            yield item
