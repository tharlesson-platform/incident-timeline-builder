from __future__ import annotations

from normalizers.timestamps import parse_timestamp


def summarize(events: list[dict], incidents: list[dict]) -> dict:
    counts_by_type: dict[str, int] = {}
    counts_by_severity: dict[str, int] = {}
    counts_by_source: dict[str, int] = {}
    counts_by_tag: dict[str, int] = {}
    services: set[str] = set()
    for event in events:
        counts_by_type[event["type"]] = counts_by_type.get(event["type"], 0) + 1
        counts_by_severity[event["severity"]] = counts_by_severity.get(event["severity"], 0) + 1
        counts_by_source[event["source"]] = counts_by_source.get(event["source"], 0) + 1
        if event.get("service"):
            services.add(event["service"])
        for tag in event.get("tags", []):
            counts_by_tag[tag] = counts_by_tag.get(tag, 0) + 1

    timeframe = {}
    if events:
        start = parse_timestamp(events[0]["timestamp"])
        end = parse_timestamp(events[-1]["timestamp"])
        timeframe = {
            "start": events[0]["timestamp"],
            "end": events[-1]["timestamp"],
            "duration_minutes": int((end - start).total_seconds() / 60),
        }

    return {
        "counts_by_type": counts_by_type,
        "counts_by_severity": counts_by_severity,
        "counts_by_source": counts_by_source,
        "counts_by_tag": dict(sorted(counts_by_tag.items())),
        "impacted_services": sorted(services),
        "total_events": len(events),
        "total_incidents": len(incidents),
        "timeframe": timeframe,
    }
