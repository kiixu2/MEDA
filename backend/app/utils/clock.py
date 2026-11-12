from datetime import date, datetime, timezone


def utcnow() -> datetime:
    """UTC الآن (بدون tzinfo ليتوافق مع ما يخزنه SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calculate_age(dob: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def is_minor(dob: date) -> bool:
    return calculate_age(dob) < 18
