from datetime import date

from entitykb.models import Entity


class Date(Entity):

    __slots__ = (
        "key",
        "name",
        "label",
        "synonyms",
        "meta",
        "year",
        "month",
        "day",
    )

    def __init__(
        self,
        *,
        year: int = None,
        month: int = None,
        day: int = None,
        meta: dict = None,
        **kwargs,
    ):
        self.year = year or meta.pop("year")
        self.month = month or meta.pop("month")
        self.day = day or meta.pop("day")

        if "name" not in kwargs:
            kwargs["name"] = self.as_date.strftime("%Y-%m-%d")

        kwargs = {"label": "DATE", **kwargs}
        super().__init__(meta=meta, **kwargs)

    @property
    def as_date(self) -> date:
        return date(self.year, self.month, self.day)
