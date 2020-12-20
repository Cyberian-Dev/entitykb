import datetime

from entitykb.contrib.date import Date
from entitykb import Node, Registry


def test_create_from_dict_via_label_to_date():
    registry = Registry.instance()
    date = registry.create(Node, dict(year=2000, month=1, day=2, label="DATE"))
    check_date(date)


def test_create_from_dict_via_cls():
    registry = Registry.instance()
    date = registry.create(Date, dict(year=2000, month=1, day=2))
    check_date(date)


def test_init_date():
    date = Date(year=2000, month=1, day=2)
    check_date(date)


def check_date(date):
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
