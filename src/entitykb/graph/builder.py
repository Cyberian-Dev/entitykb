from .model import (
    Criteria,
    AttrCriteria,
    RelCriteria,
    Query,
    FilterStep,
    WalkStep,
    Direction,
)


class QueryBuilder(object):
    def __init__(self):
        self.query = Query()

    # walk nodes

    def all_nodes(self, *tags: str, max_hops: int = 1, passthru: bool = False):
        return self._walk_nodes(
            *tags,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.outgoing, Direction.incoming)
        )

    def out_nodes(self, *tags: str, max_hops: int = 1, passthru: bool = False):
        return self._walk_nodes(
            *tags,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.outgoing,)
        )

    def in_nodes(self, *tags: str, max_hops: int = 1, passthru: bool = False):
        return self._walk_nodes(
            *tags,
            max_hops=max_hops,
            passthru=passthru,
            directions=(Direction.incoming,)
        )

    # filter

    def keep(self, *criteria, all=False):
        return self._add_filter(*criteria, all=all, exclude=False)

    def remove(self, *criteria, all=False):
        return self._add_filter(*criteria, all=all, exclude=True)

    # private functions

    def _add_filter(
        self, *criteria: Criteria, all: bool = False, exclude: bool = False
    ):
        filter = FilterStep(criteria=criteria, all=all, exclude=exclude)
        self.query.steps.append(filter)
        return self

    def _walk_nodes(
        self,
        *tags: str,
        max_hops: int = None,
        passthru: bool = False,
        directions=None
    ):
        walk = WalkStep(
            tags=tags,
            directions=Direction.as_tuple(directions, all_if_none=True),
            max_hops=max_hops,
            passthru=passthru,
        )
        self.query.steps.append(walk)
        return self

    # limit (and offset)

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
A = AttrCriteria
R = RelCriteria
