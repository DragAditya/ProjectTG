"""Miscellaneous helper functions for the Telegram Group Management Bot.

This module provides utilities to parse human-friendly durations, format
timedeltas in a readable way, and escape HTML for safe display in
Telegram messages.
"""
import html
import re
from datetime import timedelta
from typing import Optional


def parse_duration(duration_str: str) -> timedelta:
    """Parse a human-friendly duration string into a timedelta.

    Supported suffixes:
    - s: seconds
    - m: minutes
    - h: hours
    - d: days
    - w: weeks

    Example::

        parse_duration("5m")  # => datetime.timedelta(minutes=5)
        parse_duration("2h30m")  # => datetime.timedelta(hours=2, minutes=30)

    If the input is invalid or empty, a zero timedelta is returned.

    Args:
        duration_str: The duration string to parse.

    Returns:
        A timedelta corresponding to the parsed duration.
    """
    pattern = re.compile(r"(\d+)([smhdw])", re.IGNORECASE)
    matches = pattern.findall(duration_str or "")
    if not matches:
        return timedelta(0)

    total_seconds = 0
    for value_str, unit in matches:
        value = int(value_str)
        unit = unit.lower()
        if unit == "s":
            total_seconds += value
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "d":
            total_seconds += value * 86400
        elif unit == "w":
            total_seconds += value * 604800
    return timedelta(seconds=total_seconds)


def humanize_timedelta(delta: timedelta) -> str:
    """Convert a timedelta into a human-readable string.

    The output omits zero-value units and pluralizes as appropriate.

    Args:
        delta: The timedelta to format.

    Returns:
        A human-readable representation, such as ``"2 hours, 3 minutes"``.
    """
    seconds = int(delta.total_seconds())
    if seconds <= 0:
        return "0 seconds"
    parts = []
    for unit_name, unit_seconds in [
        ("week", 604800),
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]:
        if seconds >= unit_seconds:
            count, seconds = divmod(seconds, unit_seconds)
            parts.append(f"{count} {unit_name}{'s' if count != 1 else ''}")
    return ", ".join(parts)


def escape_html(text: Optional[str]) -> str:
    """Escape HTML entities for safe display in Telegram messages.

    Args:
        text: Raw text that may contain HTML characters.

    Returns:
        The escaped text suitable for ``parse_mode=HTML``.
    """
    return html.escape(text or "")