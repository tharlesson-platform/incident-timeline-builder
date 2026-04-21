from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


FALLBACK_TIMEZONES = {
    "UTC": timezone.utc,
    "Etc/UTC": timezone.utc,
    "GMT": timezone.utc,
    "America/Sao_Paulo": timezone(timedelta(hours=-3)),
}


def parse_timestamp(value: str) -> datetime:
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"

    try:
        numeric_value = float(cleaned)
    except ValueError:
        numeric_value = None

    if numeric_value is not None:
        return datetime.fromtimestamp(numeric_value, tz=timezone.utc)

    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def normalize_timestamp(value: str, target_timezone: str) -> str:
    return parse_timestamp(value).astimezone(_resolve_timezone(target_timezone)).isoformat()


def _resolve_timezone(target_timezone: str):
    try:
        return ZoneInfo(target_timezone)
    except ZoneInfoNotFoundError:
        if target_timezone in FALLBACK_TIMEZONES:
            return FALLBACK_TIMEZONES[target_timezone]
        raise
