from __future__ import annotations

from datetime import date, datetime, timedelta
import calendar
from typing import Optional


SUPPORTED_RECURRENCES = {
    "none",
    "daily",
    "weekly",
    "biweekly",
    "monthly",
    "quarterly",
    "yearly",
}


def normalize_recurrence(value: str) -> str:
    """Normalize a user-provided recurrence string to a supported keyword.

    Raises ValueError if unsupported.
    """
    v = (value or "none").strip().lower()
    aliases = {
        "once": "none",
        "one-time": "none",
        "one time": "none",
        "oneoff": "none",
        "one-off": "none",
        "week": "weekly",
        "bi-weekly": "biweekly",
        "2w": "biweekly",
        "mo": "monthly",
        "month": "monthly",
        "q": "quarterly",
        "quarter": "quarterly",
        "3mo": "quarterly",
        "yr": "yearly",
        "year": "yearly",
        "annual": "yearly",
    }
    v = aliases.get(v, v)
    if v not in SUPPORTED_RECURRENCES:
        raise ValueError(
            f"Unsupported recurrence: {value}. Supported: {', '.join(sorted(SUPPORTED_RECURRENCES))}"
        )
    return v


def parse_yyyy_mm(text: str) -> tuple[int, int]:
    year_str, month_str = text.split("-")
    return int(year_str), int(month_str)


def parse_date(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def format_date(d: Optional[date]) -> Optional[str]:
    return d.isoformat() if d else None


def add_months(d: date, months: int) -> date:
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # Handle Feb 29 → Feb 28 on non-leap years
        return d.replace(month=2, day=28, year=d.year + years)


def next_after(d: date, recurrence: str) -> date:
    r = normalize_recurrence(recurrence)
    if r == "none":
        return d
    if r == "daily":
        return d + timedelta(days=1)
    if r == "weekly":
        return d + timedelta(weeks=1)
    if r == "biweekly":
        return d + timedelta(weeks=2)
    if r == "monthly":
        return add_months(d, 1)
    if r == "quarterly":
        return add_months(d, 3)
    if r == "yearly":
        return add_years(d, 1)
    raise ValueError(f"Unsupported recurrence: {recurrence}")


def compute_next_due_date(
    current_due: Optional[date],
    start_date: Optional[date],
    recurrence: str,
    from_date: Optional[date] = None,
) -> Optional[date]:
    """Compute the next due date strictly after from_date for a schedule.

    - If recurrence is none, returns current_due or start_date.
    - Otherwise, advances until the next due date is > from_date.
    """
    r = normalize_recurrence(recurrence)
    if r == "none":
        return current_due or start_date

    base = current_due or start_date
    if base is None:
        return None

    ref = from_date or date.today()
    next_due = base
    while next_due <= ref:
        next_due = next_after(next_due, r)
    return next_due
