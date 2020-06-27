from datetime import date

from entitykb.date.grammar import parse_date, is_prefix


def test_parse_examples():
    assert parse_date("2019-01-02") == date(2019, 1, 2)
    assert parse_date("JAN 2019-02") == date(2019, 1, 2)
    assert parse_date("2019 JAN, 02") == date(2019, 1, 2)

    assert parse_date("2019 JAN") is None
    assert parse_date("2019 01") is None
    assert parse_date("2019 01") is None

    assert parse_date("15 SEP 2019") == date(2019, 9, 15)
    assert parse_date("15 SEPT 2019") == date(2019, 9, 15)
    assert parse_date("15 SEPTEMBER 2019") == date(2019, 9, 15)

    assert parse_date("20190102") is None


def test_is_prefix():
    assert is_prefix("2019-01-02") is True
    assert is_prefix("2019-01-") is True
    assert is_prefix("2019-01") is True
    assert is_prefix("2019-") is True
    assert is_prefix("2019") is True

    assert is_prefix("JAN 2019-02") is True
    assert is_prefix("JAN 2019-") is True
    assert is_prefix("JAN 2019") is True
    assert is_prefix("JAN ") is True
    assert is_prefix("JAN") is True
