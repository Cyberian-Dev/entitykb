from typing import Set, Iterable

from .model import (
    Node,
    Query,
    WalkStep,
    FilterStep,
    Filter,
    Direction,
    ensure_iterable,
)


class QueryBuilder(object):
    def __init__(self, starts=None, *args):
        starts = starts or args
        self.query = Query(starts=starts, steps=[])

    # steps (returns self)

    def walk(
        self,
        *tags: str,
        directions: Direction = Direction.incoming,
        max_hops: int = None,
        passthru: bool = False,
    ):
        walk = WalkStep(
            tags=tags,
            directions=directions,
            max_hops=max_hops,
            passthru=passthru,
        )
        self.query.steps.append(walk)
        return self

    def filter(
        self,
        *,
        filters: Iterable = None,
        label: str = None,
        labels: Set[str] = None,
        directions=Direction.incoming,
        self_ok: bool = False,
        _exclude: bool = False,
        **kwargs,
    ):
        # prep step
        filters = ensure_iterable(filters) if filters else []

        labels = list(ensure_iterable(labels or []))
        if label:
            labels.append(label)

        tags = []
        keys = []
        for tag, node in kwargs.items():
            tags.append(tag)
            keys.append(Node.to_key(node))

        if labels or tags:
            f = Filter(
                labels=labels,
                tags=tags,
                keys=keys,
                directions=directions,
                self_ok=self_ok,
            )
            filters.append(f)

        if filters:
            filter_step = FilterStep(filters=filters, exclude=_exclude)
            self.query.steps.append(filter_step)

        return self

    def exclude(self, **kwargs):
        self.filter(_exclude=True, **kwargs)
        return self

    # goals (return query)

    def all(self):
        self.query.limit = None
        return self.query

    def limit(self, limit: int):
        self.query.limit = limit
        return self.query

    def first(self):
        self.query.limit = 1
        return self.query

    def page(self, number: int = 0, size: int = 20):
        offset = number * size
        self.query.offset = offset
        self.query.limit = size
        return self.query


QB = QueryBuilder
