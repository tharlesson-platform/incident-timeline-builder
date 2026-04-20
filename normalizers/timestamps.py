from __future__ import annotations

from datetime import datetime


def normalize_timestamp(value: str) -> str:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
