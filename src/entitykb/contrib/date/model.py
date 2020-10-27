from datetime import date

from entitykb.models import Entity


class Date(Entity):

    __slots__ = (
        "key",
        "name",
        "label",
        "data",
        "synonyms",
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
        **kwargs,
    ):
        self.year = year
        self.month = month
        self.day = day

        if "name" not in kwargs:
            kwargs["name"] = self.as_date.strftime("%Y-%m-%d")

        kwargs = {"label": "DATE", **kwargs}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Date: year={self.year} month={self.month} day={self.day}>"

    @property
    def as_date(self) -> date:
        return date(self.year, self.month, self.day)
