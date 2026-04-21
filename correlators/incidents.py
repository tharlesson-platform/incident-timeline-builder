from __future__ import annotations

from datetime import timedelta
from typing import Any

from normalizers.timestamps import parse_timestamp


SEVERITY_PRIORITY = {"critical": 3, "error": 2, "warning": 1, "info": 0}
GENERIC_TAGS = {
    "alert",
    "alb",
    "build",
    "chatops",
    "cloudwatch",
    "customer-impact",
    "deploy",
    "github-actions",
    "info",
    "pipeline",
    "probe",
    "recovery",
    "rollback",
    "slack",
    "terraform",
    "validation",
}
CLUSTER_WINDOW = timedelta(hours=2)


def group_incidents(events: list[dict]) -> list[dict]:
    clusters: list[dict[str, Any]] = []
    explicit_clusters: dict[str, dict[str, Any]] = {}

    for event in sorted(events, key=lambda item: item["timestamp"]):
        explicit_id = event.get("incident_id")
        cluster = explicit_clusters.get(explicit_id) if explicit_id else None
        if cluster is None:
            cluster = _find_matching_cluster(clusters, event)
        if cluster is None:
            cluster = _create_cluster(event, sequence=len(clusters) + 1)
            clusters.append(cluster)
        _attach_event(cluster, event)
        explicit_id = event.get("incident_id")
        if explicit_id:
            explicit_clusters[explicit_id] = cluster

    return [_finalize_cluster(cluster) for cluster in clusters]


def select_primary_incident(incidents: list[dict]) -> dict | None:
    if not incidents:
        return None
    return max(
        incidents,
        key=lambda incident: (
            incident["customer_impact_events"],
            SEVERITY_PRIORITY.get(incident["severity"], 0),
            incident["event_count"],
        ),
    )


def _find_matching_cluster(clusters: list[dict[str, Any]], event: dict) -> dict[str, Any] | None:
    event_time = parse_timestamp(event["timestamp"])
    candidates: list[tuple[int, float, dict[str, Any]]] = []
    for cluster in clusters:
        delta = abs((event_time - cluster["last_seen"]).total_seconds())
        if delta > CLUSTER_WINDOW.total_seconds():
            continue
        score = _cluster_score(cluster, event)
        if score > 0:
            candidates.append((score, -delta, cluster))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return candidates[0][2]


def _cluster_score(cluster: dict[str, Any], event: dict) -> int:
    score = 0
    event_tags = set(event.get("tags", []))
    event_service = event.get("service")
    if event_service and event_service in cluster["services"]:
        score += 4
    shared_tags = set(_meaningful_tags(event_tags)) & cluster["meaningful_tags"]
    score += 2 * len(shared_tags)
    if event.get("incident_id") and event["incident_id"] == cluster["incident_id"]:
        score += 10
    if "customer-impact" in event_tags and cluster["customer_impact_events"] > 0:
        score += 2
    return score


def _create_cluster(event: dict, sequence: int) -> dict[str, Any]:
    event_time = parse_timestamp(event["timestamp"])
    had_explicit_id = bool(event.get("incident_id"))
    incident_id = event.get("incident_id") or _generate_incident_id(event, sequence)
    event["incident_id"] = incident_id
    return {
        "incident_id": incident_id,
        "events": [],
        "sources": set(),
        "services": set(),
        "tags": set(),
        "meaningful_tags": set(),
        "owners": set(),
        "first_seen": event_time,
        "last_seen": event_time,
        "customer_impact_events": 0,
        "severity_rank": SEVERITY_PRIORITY.get(event.get("severity", "info"), 0),
        "correlation_reason": "explicit incident_id" if had_explicit_id else "shared tags and time proximity",
    }


def _generate_incident_id(event: dict, sequence: int) -> str:
    event_time = parse_timestamp(event["timestamp"])
    primary_tag = next(iter(_meaningful_tags(event.get("tags", []))), None)
    primary_service = event.get("service")
    slug = (primary_service or primary_tag or event.get("source") or "incident").lower()
    slug = "".join(character for character in slug if character.isalnum() or character == "-").strip("-") or "incident"
    return f"auto-{slug}-{event_time:%Y%m%d%H%M}-{sequence:02d}"


def _attach_event(cluster: dict[str, Any], event: dict) -> None:
    event["incident_id"] = cluster["incident_id"]
    cluster["events"].append(event)
    cluster["sources"].add(event.get("source", "unknown"))
    if event.get("service"):
        cluster["services"].add(event["service"])
    cluster["tags"].update(event.get("tags", []))
    cluster["meaningful_tags"].update(_meaningful_tags(event.get("tags", [])))
    if event.get("owner"):
        cluster["owners"].add(event["owner"])
    if "customer-impact" in event.get("tags", []):
        cluster["customer_impact_events"] += 1
    event_time = parse_timestamp(event["timestamp"])
    if event_time < cluster["first_seen"]:
        cluster["first_seen"] = event_time
    if event_time > cluster["last_seen"]:
        cluster["last_seen"] = event_time
    cluster["severity_rank"] = max(cluster["severity_rank"], SEVERITY_PRIORITY.get(event.get("severity", "info"), 0))


def _meaningful_tags(tags: list[str] | set[str]) -> list[str]:
    return [tag for tag in tags if tag not in GENERIC_TAGS and not tag.startswith(("environment:", "channel:"))]


def _finalize_cluster(cluster: dict[str, Any]) -> dict:
    events = sorted(cluster["events"], key=lambda item: item["timestamp"])
    probable_cause = next(
        (event["message"] for event in events if event["severity"] in {"critical", "error"}),
        "indeterminate",
    )
    severity = _severity_from_rank(cluster["severity_rank"])
    duration = int((cluster["last_seen"] - cluster["first_seen"]).total_seconds() / 60)
    return {
        "incident_id": cluster["incident_id"],
        "title": _build_title(cluster, probable_cause),
        "status": _status_from_events(events),
        "severity": severity,
        "probable_cause": probable_cause,
        "start": events[0]["timestamp"],
        "end": events[-1]["timestamp"],
        "duration_minutes": duration,
        "event_count": len(events),
        "customer_impact_events": cluster["customer_impact_events"],
        "sources": sorted(cluster["sources"]),
        "services": sorted(cluster["services"]),
        "tags": sorted(cluster["tags"]),
        "owners": sorted(cluster["owners"]),
        "correlation_reason": cluster["correlation_reason"],
        "events": events,
    }


def _severity_from_rank(rank: int) -> str:
    for severity, value in SEVERITY_PRIORITY.items():
        if value == rank:
            return severity
    return "info"


def _status_from_events(events: list[dict]) -> str:
    for event in reversed(events):
        message = event.get("message", "").lower()
        if any(keyword in message for keyword in ("recovered", "healthy", "rollback completed", "resolved")):
            return "mitigated"
        if "rollback" in event.get("tags", []):
            return "mitigated"
    if any(event.get("severity") == "critical" for event in events):
        return "investigating"
    return "observed"


def _build_title(cluster: dict[str, Any], probable_cause: str) -> str:
    service = next(iter(sorted(cluster["services"])), None)
    if service:
        return f"{service} incident"
    if probable_cause != "indeterminate":
        return probable_cause[:80]
    return cluster["incident_id"]
