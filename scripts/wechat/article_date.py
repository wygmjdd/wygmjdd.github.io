"""Validation for article dates used by the WeChat import pipeline."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

CHINA_TIMEZONE = timezone(timedelta(hours=8))
EARLIEST_PLAUSIBLE_ARTICLE_DATE = date(2000, 1, 1)


def current_china_date() -> date:
    return datetime.now(CHINA_TIMEZONE).date()


def validate_article_date(
    value: str,
    *,
    source: str,
    today: date | None = None,
) -> date:
    """Return a parsed date or reject values that must not reach Hugo output."""
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid article date {value!r} from {source}; "
            "expected a real YYYY-MM-DD date. Refusing to generate content."
        ) from exc

    current = today or current_china_date()
    if parsed < EARLIEST_PLAUSIBLE_ARTICLE_DATE:
        raise ValueError(
            f"Implausible article date {value!r} from {source}: dates before "
            f"{EARLIEST_PLAUSIBLE_ARTICLE_DATE.isoformat()} are not allowed. "
            "Refusing to generate content."
        )
    if parsed > current:
        raise ValueError(
            f"Implausible article date {value!r} from {source}: future dates are "
            f"not allowed (current China date: {current.isoformat()}). "
            "Refusing to generate content."
        )
    return parsed
