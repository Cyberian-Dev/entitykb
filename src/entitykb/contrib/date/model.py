from typing import Any
from datetime import date

from entitykb import Entity


class Date(Entity):
    year: int = None
    month: int = None
    day: int = None

    def __init__(self, **data: Any):
        dt = date(data["year"], data["month"], data["day"])
        data.setdefault("name", dt.strftime("%Y-%m-%d"))
        super().__init__(**data)

    @property
    def as_date(self) -> date:
        return date(self.year, self.month, self.day)
