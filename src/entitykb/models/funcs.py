import re

camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name, upper=False):
    name = camel_pattern.sub("_", name)
    name = name.upper() if upper else name.lower()
    return name


def is_iterable(items):
    return isinstance(items, (list, set, dict, frozenset, tuple))


def ensure_iterable(items, f=None, explode_first=False):
    f = f or tuple

    if not is_iterable(items):
        items = f((items,))

    elif explode_first and len(items) == 1:
        first_item = next(iter(items))
        if is_iterable(first_item):
            items = f(first_item)

    return items


def under_limit(items, limit: int):
    if limit is None:
        return True

    return len(items) < limit


def label_filter(labels):
    labels = set(ensure_iterable(labels))

    def is_label(key):
        _, label = key.rsplit("|", 1)
        return label in labels

    if labels:
        return is_label
