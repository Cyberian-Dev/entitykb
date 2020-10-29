import datetime

from entitykb.contrib.date import Date
from entitykb import Node


def test_create_from_dict_via_label_to_date():
    date = Node.create(dict(year=2000, month=1, day=2, label="DATE"))
    assert isinstance(date, Date)
    assert date.year == 2000
    assert date.month == 1
    assert date.day == 2
    assert date.name == "2000-01-02"
    assert date.label == "DATE"
    assert date.key == "2000-01-02|DATE"
    assert date.as_date == datetime.date(2000, 1, 2)


def test_create_from_dict_via_cls():
    date = Date.create(dict(year=2000, month=1, day=2))
    assert isinstance(date, Date)
    assert date.year == 2000
    assert date.month == 1
    assert date.day == 2
    assert date.name == "2000-01-02"
    assert date.label == "DATE"
    assert date.key == "2000-01-02|DATE"
    assert date.as_date == datetime.date(2000, 1, 2)


def test_init_date():
    date = Date(year=2000, month=1, day=2)
    assert isinstance(date, Date)
    assert date.year == 2000
    assert date.month == 1
    assert date.day == 2
    assert date.name == "2000-01-02"
    assert date.label == "DATE"
    assert date.key == "2000-01-02|DATE"
    assert date.as_date == datetime.date(2000, 1, 2)
    assert date.dict() == dict(
        name="2000-01-02",
        key="2000-01-02|DATE",
        year=2000,
        month=1,
        day=2,
        label="DATE",
        synonyms=(),
        data=None,
    )
