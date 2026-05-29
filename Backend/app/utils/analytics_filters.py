from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta


def validate_year_month(*, year: int, month: int) -> None:
    if year < 2000 or year > 2100:
        raise ValueError("year must be between 2000 and 2100")
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")


def resolve_weekly_window(*, end_date: date | None = None, days: int = 7) -> tuple[date, date]:
    if days < 2 or days > 31:
        raise ValueError("days must be between 2 and 31")
    end = end_date or date.today()
    start = end - timedelta(days=days - 1)
    return start, end


def month_date_range(*, year: int, month: int) -> tuple[date, date]:
    validate_year_month(year=year, month=month)
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end

