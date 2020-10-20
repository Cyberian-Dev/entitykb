import datetime

from entitykb.contrib.date import Date
from entitykb import Entity


def test_from_dict():
    d = dict(name="2000-01-02", year=2000, month=1, day=2)
    entity = Entity.create(d)
    assert entity.attrs == dict(year=2000, month=1, day=2)
    assert repr(entity) == "<Entity: name=2000-01-02, label=ENTITY>"

    date = Date.create(d)
    assert date.year == 2000
    assert date.month == 1
    assert date.day == 2
    assert date.meta is None
    assert repr(date) == "<Entity: name=2000-01-02, label=DATE>"


def test_date():
    date = Date(year=2001, month=2, day=3)
    assert date.name == "2001-02-03"
    assert date.as_date == datetime.date(2001, 2, 3)
    assert date.dict() == dict(
        name="2001-02-03",
        key="2001-02-03|DATE",
        year=2001,
        month=2,
        day=3,
        label="DATE",
        meta=None,
        synonyms=(),
    )
