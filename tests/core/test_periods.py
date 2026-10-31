from src.enums import PeriodType
from datetime import date as Date
from src.core.periods import calculate_period
import pytest

def test_calculate_period_day():
    today = Date.today()
    date_from, date_to = calculate_period(PeriodType.day, today)

    assert date_from == today
    assert date_to == today

def test_calculate_period_week():
    data = Date(2026, 10, 31)
    date_from, date_to = calculate_period(PeriodType.week, data)

    assert date_from == Date(2026, 10, 26)
    assert date_to == Date(2026, 11, 1)


def test_calculate_period_month():
    data = Date(2026, 10, 31)
    date_from, date_to = calculate_period(PeriodType.month, data)

    assert date_from == Date(2026, 10, 1)
    assert date_to == Date(2026, 10, 31)

def test_calculate_period_year():

    data = Date(2026, 10, 31)
    date_from, date_to = calculate_period(PeriodType.year, data)

    assert date_from == Date(2026, 1, 1)
    assert date_to == Date(2026, 12, 31)

def test_calculate_period_week_between_years():

    data = Date(2026, 12, 30)
    date_from, date_to = calculate_period(PeriodType.week, data)

    assert date_from == Date(2026, 12, 28)
    assert date_to == Date(2027, 1, 3)

def test_calculate_period_week_february():

    data = Date(2026, 2, 28)
    date_from, date_to = calculate_period(PeriodType.week, data)

    assert date_from == Date(2026, 2, 23)
    assert date_to == Date(2026, 3, 1)

def test_calculate_period_week_february_leap_year():

    data = Date(2028, 2, 29)
    date_from, date_to = calculate_period(PeriodType.week, data)

    assert date_from == Date(2028, 2, 28)
    assert date_to == Date(2028, 3, 5)

def test_calculate_period_month_february():

    data = Date(2026, 2, 15)
    date_from, date_to = calculate_period(PeriodType.month, data)

    assert date_from == Date(2026, 2, 1)
    assert date_to == Date(2026, 2, 28)

def test_calculate_period_month_february_leap_year():

    data = Date(2028, 2, 15)
    date_from, date_to = calculate_period(PeriodType.month, data)

    assert date_from == Date(2028, 2, 1)
    assert date_to == Date(2028, 2, 29)