from datetime import date
from entitykb.contrib.date import DateResolver, Date

resolver = DateResolver()


def parse_date(s):
    entities = resolver.resolve(s)
    if entities:
        d: Date = entities[0]
        return d.as_date


def test_is_relevant():
    assert DateResolver.is_relevant(None)
    assert DateResolver.is_relevant([])
    assert DateResolver.is_relevant(["DATE", "EMAIL"])
    assert not DateResolver.is_relevant(["EMAIL"])


def test_is_prefix():
    assert resolver.is_prefix("January 1 2019") is True
    assert resolver.is_prefix("January 1,") is True
    assert resolver.is_prefix("January") is True

    assert resolver.is_prefix("January 1st,") is True

    assert resolver.is_prefix("2019-01-02") is True
    assert resolver.is_prefix("2019-01-") is True
    assert resolver.is_prefix("2019-01") is True
    assert resolver.is_prefix("2019-") is True
    assert resolver.is_prefix("2019") is True

    assert resolver.is_prefix("JAN ") is True
    assert resolver.is_prefix("JAN") is True

    assert resolver.is_prefix("01/02/22") is True
    assert resolver.is_prefix("01/02/") is True
    assert resolver.is_prefix("01/02") is True
    assert resolver.is_prefix("01/") is True


def test_is_not_prefix():
    assert resolver.is_prefix("JAN 2019") is False
    assert resolver.is_prefix("JAN JAN JAN") is False


def test_parse_m_d_y():
    assert parse_date("SEP 15 2019") == date(2019, 9, 15)
    assert parse_date("SEP 15th 2019") == date(2019, 9, 15)
    assert parse_date("SEP 15th, 2019") == date(2019, 9, 15)
    assert parse_date("SEPT 15 2019") == date(2019, 9, 15)
    assert parse_date("SEPTEMBER 15 2019") == date(2019, 9, 15)
    assert parse_date("09/15/2019") == date(2019, 9, 15)
    assert parse_date("09/15/19") == date(2019, 9, 15)

    # MDY > DMY
    assert parse_date("12/11/2019") == date(2019, 12, 11)


def test_fix_year():
    assert parse_date("12/11/99") == date(1999, 12, 11)
    assert parse_date("12/11/19") == date(2019, 12, 11)


def test_parse_d_m_y():
    assert parse_date("15 SEP 2019") == date(2019, 9, 15)
    assert parse_date("15 SEPT 2019") == date(2019, 9, 15)
    assert parse_date("15 SEPTEMBER 2019") == date(2019, 9, 15)
    assert parse_date("15 SEPTEMBER 19") == date(2019, 9, 15)

    assert parse_date("1st SEP 2019") == date(2019, 9, 1)
    assert parse_date("3rd SEP 2019") == date(2019, 9, 3)
    assert parse_date("15th SEP 2019") == date(2019, 9, 15)

    # DMY wins when D > 12
    assert parse_date("15/09/2019") == date(2019, 9, 15)
    assert parse_date("15/09/19") == date(2019, 9, 15)


def test_parse_y_m_d():
    assert parse_date("2019-01-02") == date(2019, 1, 2)
    assert parse_date("20190102") == date(2019, 1, 2)


def test_parse_incomplete():
    assert parse_date("2019 JAN") is None
    assert parse_date("2019 01") is None
    assert parse_date("2019 01") is None
    assert parse_date("2019-01-") is None
    assert parse_date("2019-01-0") is None


def test_failure_cases():
    assert parse_date("2019-13-13") is None
