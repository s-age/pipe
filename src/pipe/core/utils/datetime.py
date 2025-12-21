"""
A utility module for centralized datetime operations.
"""

from datetime import UTC, datetime, tzinfo


def get_current_datetime(tz: tzinfo = UTC) -> datetime:
    """
    Returns the current time as a timezone-aware datetime object.

    Args:
        tz: A zoneinfo.ZoneInfo object. Defaults to UTC.

    Returns:
        A timezone-aware datetime object.
    """
    return datetime.now(tz)


def get_current_timestamp(tz: tzinfo = UTC, fmt: str | None = None) -> str:
    """
    Returns the current time as a timezone-aware formatted string.

    If a format string (fmt) is provided, it uses strftime.
    Otherwise, it returns the time in ISO 8601 format.

    Args:
        tz: A zoneinfo.ZoneInfo object. Defaults to UTC.
        fmt: An optional format string for strftime.

    Returns:
        The current timestamp as a string.
    """
    now = get_current_datetime(tz)
    if fmt:
        return now.strftime(fmt)
    else:
        return now.isoformat()
