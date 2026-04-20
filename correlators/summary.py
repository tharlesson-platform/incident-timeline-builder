from __future__ import annotations


def summarize(events: list[dict]) -> dict:
    counts_by_type: dict[str, int] = {}
    counts_by_severity: dict[str, int] = {}
    for event in events:
        counts_by_type[event["type"]] = counts_by_type.get(event["type"], 0) + 1
        counts_by_severity[event["severity"]] = counts_by_severity.get(event["severity"], 0) + 1
    return {
        "counts_by_type": counts_by_type,
        "counts_by_severity": counts_by_severity,
    }
