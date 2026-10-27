from src.enums import PeriodType
from datetime import date as Date, timedelta
from calendar import monthrange

def calculate_period(period: PeriodType, reference_date: Date | None = None) -> tuple[Date, Date]:
    if not isinstance(period, PeriodType): #sprawdza czy argument period jest wartoscia klasy PeriodType
        raise ValueError("Invalid period type")
    if reference_date is None:
        reference_date = Date.today()

    date_from = reference_date
    date_to = reference_date

    if period == PeriodType.week:
        date_from = reference_date - timedelta(days=reference_date.weekday())
        date_to = date_from + timedelta(days=6)

    elif period == PeriodType.month:
        date_from = Date(reference_date.year, reference_date.month, 1) # pierwszy dzien biezacego miesiaca
        last_day = monthrange(reference_date.year, reference_date.month)[1]
        date_to = Date(reference_date.year, reference_date.month, last_day)

    elif period == PeriodType.year:
        date_from = Date(reference_date.year, 1, 1)
        date_to = Date(reference_date.year, 12, 31)

    return date_from, date_to