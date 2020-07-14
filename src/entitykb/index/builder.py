from typing import Set
from . import Query, QueryStart, QueryGoal, WalkStep, FilterStep, LabelFilter


class QueryBuilder(object):
    def __init__(self, *entities: str, iterables=None):
        start = QueryStart(entities=entities, iterables=iterables)
        self.query = Query(start=start)

    # steps (returns self)

    def walk(
        self,
        *tags: str,
        incoming: bool = True,
        max_hops: int = None,
        passthru: bool = False,
    ):
        walk = WalkStep(
            tags=tags, incoming=incoming, max_hops=max_hops, passthru=passthru,
        )
        self.query.steps.append(walk)
        return self

    def filter(self, labels: Set[str] = None, exclude: bool = False, **_):
        if labels:
            label_filter = LabelFilter(labels=labels)
            filter_step = FilterStep(filters=[label_filter], exclude=exclude)
            self.query.steps.append(filter_step)

        return self

    def exclude(self, **kwargs):
        self.filter(exclude=True, **kwargs)
        return self

    # goals (return query)

    def all(self):
        self.query.goal = QueryGoal()
        return self.query

    def limit(self, limit: int):
        self.query.goal = QueryGoal(limit=limit)
        return self.query

    def first(self):
        self.query.goal = QueryGoal(limit=1)
        return self.query


QB = QueryBuilder
