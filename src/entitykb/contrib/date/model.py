from typing import Any
from datetime import date

from entitykb import Entity


class Date(Entity):
    year: int = None
    month: int = None
    day: int = None
    text: str = None

    def __init__(self, **data: Any):
        year = data.get("year")
        month = data.get("month")
        day = data.get("day")
        if day and 0 < day <= 31:
            name = f"{year:0>4}-{month:0>2}-{day:0>2}"
        else:
            name = f"{year:0>4}-{month:0>2}"

        data.setdefault("name", name)
        super().__init__(**data)

    @property
    def as_date(self) -> date:
        return date(self.year, self.month, self.day or 1)
