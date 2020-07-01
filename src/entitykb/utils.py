import sys
import datetime
import functools
import os
import tempfile

from importlib import import_module
from typing import Union


@functools.lru_cache(maxsize=100)
def get_class_from_name(full_name: str):
    module_name, class_name = full_name.rsplit(".", 1)
    module = import_module(module_name)
    klass = getattr(module, class_name)
    return klass


def instantiate_class_from_name(full_name: str, *args, **kwargs):
    klass = get_class_from_name(full_name)
    return klass(*args, **kwargs)


def get_class_name_from_instance(obj: object):
    return f"{obj.__module__}.{obj.__class__.__name__}" if obj else None


def tupilify(values: Union[list, tuple, set]) -> tuple:
    """ Converts values to a sorted, unique tuple. """
    if values:
        values = tuple(sorted(set(values)))
    else:
        values = tuple()
    return values


def sizeof_fmt(num, suffix="B"):
    # https://stackoverflow.com/a/1094933/1946790
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%.2f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.2f %s%s" % (num, "Yi", suffix)


def sizeof(path_or_obj):
    try:
        num = os.path.getsize(path_or_obj)
    except FileNotFoundError:
        num = 0
    except TypeError:
        num = sys.getsizeof(path_or_obj)
    return sizeof_fmt(num)


def file_updated(path) -> datetime:
    if path and os.path.exists(path):
        file_t = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(file_t)


def safe_write(path: str, data: bytes):
    """ Write data to temporary file. Then use os.link to move into place. """
    # https://stackoverflow.com/a/36784658/1946790
    # https://stackoverflow.com/a/57015098/1946790
    dir_path = os.path.dirname(path)
    with tempfile.NamedTemporaryFile(dir=dir_path, mode="w+b") as tf:
        tf.write(data)
        os.link(tf.name, path)


def generate_edits(token: str, max_token_distance: int):
    yield token, 0

    pairs = set()

    max_edit_distance = min(max_token_distance + 1, len(token) - 3)
    for edit_distance in range(1, max_edit_distance):
        for char_index in range(1, len(token) - edit_distance + 1):
            edit = token[:char_index] + token[char_index + edit_distance :]
            pair = edit, edit_distance
            if pair not in pairs:
                pairs.add(pair)
                yield pair
