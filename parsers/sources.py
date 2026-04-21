from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable


SUPPORTED_EXTENSIONS = {".csv", ".json"}
SEVERITY_PRIORITY = {"critical": 3, "error": 2, "warning": 1, "info": 0}
GENERIC_SOURCE_HINTS = {"cloudwatch", "slack", "github-actions", "alertmanager", "terraform", "jenkins"}


def load_sources(path: Path, recursive: bool = False) -> list[dict]:
    events: list[dict] = []
    for evidence_file in _iter_evidence_files(path, recursive=recursive):
        events.extend(_load_file(evidence_file))
    return events


def _iter_evidence_files(path: Path, recursive: bool) -> Iterable[Path]:
    if path.is_file():
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path
        return

    iterator = path.rglob("*") if recursive else path.iterdir()
    for child in iterator:
        if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield child


def _load_file(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        return _load_csv(path)
    return _load_json(path)


def _load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [event for row in reader if (event := _shape_generic_event(row, path=path))]


def _load_json(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [event for event in _parse_json_payload(payload, path) if event]


def _parse_json_payload(payload: Any, path: Path) -> list[dict]:
    if isinstance(payload, dict):
        if "workflow_runs" in payload:
            return [_shape_github_actions_run(item, path) for item in payload["workflow_runs"]]
        if "jobs" in payload:
            return [_shape_github_actions_job(item, path) for item in payload["jobs"]]
        if "messages" in payload:
            channel = payload.get("channel") or payload.get("name")
            return [_shape_slack_message(item, path, channel=channel) for item in payload["messages"]]
        for key in ("alarms", "metric_alarms", "cloudwatch_alarms"):
            if key in payload:
                return [_shape_cloudwatch_alarm(item, path) for item in payload[key]]
        if "events" in payload:
            return [_shape_generic_event(item, path=path) for item in payload["events"]]
        return [_shape_generic_event(payload, path=path)]

    if isinstance(payload, list):
        if _looks_like_slack_payload(payload):
            return [_shape_slack_message(item, path) for item in payload]
        if _looks_like_cloudwatch_payload(payload):
            return [_shape_cloudwatch_alarm(item, path) for item in payload]
        if _looks_like_github_actions_payload(payload):
            return [_shape_github_actions_run(item, path) for item in payload]
        return [_shape_generic_event(item, path=path) for item in payload]

    return []


def _looks_like_slack_payload(payload: list[Any]) -> bool:
    return bool(payload) and all(isinstance(item, dict) and "ts" in item and "text" in item for item in payload)


def _looks_like_cloudwatch_payload(payload: list[Any]) -> bool:
    return bool(payload) and all(
        isinstance(item, dict) and any(key in item for key in ("AlarmName", "alarm_name", "NewStateValue", "state"))
        for item in payload
    )


def _looks_like_github_actions_payload(payload: list[Any]) -> bool:
    return bool(payload) and all(
        isinstance(item, dict) and any(key in item for key in ("run_started_at", "conclusion", "workflow_id"))
        for item in payload
    )


def _shape_github_actions_run(item: dict, path: Path) -> dict | None:
    actor = item.get("actor") or {}
    workflow_name = item.get("name") or item.get("display_title") or "GitHub Actions run"
    status = item.get("conclusion") or item.get("status") or "completed"
    environment = item.get("environment")
    service = item.get("service") or _service_from_text(workflow_name)
    tags = _merge_tags(
        item.get("tags"),
        item.get("event"),
        item.get("head_branch"),
        environment,
        service,
        "github-actions",
    )
    if "deploy" in workflow_name.lower():
        tags.append("deploy")
        event_type = "deploy"
    else:
        tags.append("pipeline")
        event_type = "pipeline"
    record = {
        "timestamp": item.get("updated_at") or item.get("run_started_at") or item.get("created_at"),
        "type": item.get("type") or event_type,
        "severity": _severity_from_status(status),
        "source": "github-actions",
        "message": f"{workflow_name} ({status})",
        "tags": tags,
        "incident_id": item.get("incident_id"),
        "owner": item.get("owner") or actor.get("login"),
        "service": service,
        "status": status,
        "link": item.get("html_url"),
        "run_id": item.get("id"),
        "environment": environment,
    }
    return _shape_generic_event(record, path=path)


def _shape_github_actions_job(item: dict, path: Path) -> dict | None:
    status = item.get("conclusion") or item.get("status") or "completed"
    name = item.get("name") or "GitHub Actions job"
    record = {
        "timestamp": item.get("completed_at") or item.get("started_at"),
        "type": "pipeline",
        "severity": _severity_from_status(status),
        "source": "github-actions",
        "message": f"{name} ({status})",
        "tags": _merge_tags(item.get("tags"), item.get("runner_name"), "github-actions", "pipeline"),
        "incident_id": item.get("incident_id"),
        "owner": item.get("owner"),
        "service": item.get("service") or _service_from_text(name),
        "status": status,
        "link": item.get("html_url"),
    }
    return _shape_generic_event(record, path=path)


def _shape_cloudwatch_alarm(item: dict, path: Path) -> dict | None:
    dimensions = _dimensions_to_map(item.get("Dimensions") or item.get("dimensions"))
    alarm_name = item.get("AlarmName") or item.get("alarm_name") or item.get("name") or "CloudWatch alarm"
    state = item.get("NewStateValue") or item.get("StateValue") or item.get("state") or "ALARM"
    reason = item.get("NewStateReason") or item.get("reason") or item.get("AlarmDescription") or ""
    service = item.get("service") or dimensions.get("service") or dimensions.get("loadbalancer") or _service_from_text(alarm_name)
    tags = _merge_tags(item.get("tags"), service, dimensions.get("environment"), "cloudwatch")
    alarm_name_lower = alarm_name.lower()
    if any(keyword in alarm_name_lower for keyword in ("5xx", "latency", "availability", "error")):
        tags.append("customer-impact")
    record = {
        "timestamp": item.get("StateUpdatedTimestamp") or item.get("state_updated_timestamp") or item.get("timestamp"),
        "type": item.get("type") or "alert",
        "severity": _severity_from_status(state),
        "source": "cloudwatch",
        "message": f"{alarm_name}: {reason or state}",
        "tags": tags,
        "incident_id": item.get("incident_id"),
        "owner": item.get("owner"),
        "service": service,
        "status": state,
        "link": item.get("link"),
        "alarm_name": alarm_name,
    }
    return _shape_generic_event(record, path=path)


def _shape_slack_message(item: dict, path: Path, channel: str | None = None) -> dict | None:
    text = " ".join(str(item.get("text", "")).split())
    inferred_tags = [channel, "slack"]
    lower_text = text.lower()
    if "rollback" in lower_text:
        inferred_tags.append("rollback")
    if "deploy" in lower_text:
        inferred_tags.append("deploy")
    if any(keyword in lower_text for keyword in ("impact", "customer", "outage", "5xx", "latency", "degraded")):
        inferred_tags.append("customer-impact")
    record = {
        "timestamp": item.get("timestamp") or item.get("ts"),
        "type": item.get("type") or "chatops",
        "severity": item.get("severity") or _severity_from_text(text),
        "source": "slack",
        "message": text,
        "tags": _merge_tags(item.get("tags"), inferred_tags, item.get("service")),
        "incident_id": item.get("incident_id") or _incident_id_from_channel(channel),
        "owner": item.get("owner") or item.get("user") or item.get("username"),
        "service": item.get("service") or _service_from_text(text),
        "status": item.get("status"),
        "link": item.get("permalink"),
        "channel": channel,
        "thread_ts": item.get("thread_ts"),
    }
    return _shape_generic_event(record, path=path)


def _shape_generic_event(item: dict | None, path: Path) -> dict | None:
    if not item:
        return None

    timestamp = _first_value(
        item,
        "timestamp",
        "ts",
        "time",
        "event_time",
        "created_at",
        "updated_at",
        "run_started_at",
        "started_at",
        "completed_at",
    )
    if not timestamp:
        return None

    source = str(item.get("source") or _infer_source_from_path(path)).strip() or "unknown"
    message = str(
        item.get("message")
        or item.get("text")
        or item.get("summary")
        or item.get("title")
        or item.get("name")
        or item.get("description")
        or "event without message"
    ).strip()

    event_type = str(item.get("type") or item.get("kind") or _infer_type(source, message)).strip() or "unknown"
    severity = _normalize_severity(item.get("severity") or item.get("status") or item.get("state") or message)
    service = item.get("service") or _service_from_text(message) or _service_from_tags(item.get("tags"))
    tags = _normalize_tags(_merge_tags(item.get("tags"), item.get("labels"), service, source))
    incident_id = item.get("incident_id") or item.get("incident") or _extract_incident_id(tags)
    owner = item.get("owner") or item.get("user") or item.get("author") or item.get("triggered_by")
    link = item.get("link") or item.get("url") or item.get("html_url") or item.get("permalink")
    status = item.get("status") or item.get("state")

    consumed_keys = {
        "timestamp",
        "ts",
        "time",
        "event_time",
        "created_at",
        "updated_at",
        "run_started_at",
        "started_at",
        "completed_at",
        "source",
        "message",
        "text",
        "summary",
        "title",
        "name",
        "description",
        "type",
        "kind",
        "severity",
        "status",
        "state",
        "tags",
        "labels",
        "incident_id",
        "incident",
        "owner",
        "user",
        "author",
        "triggered_by",
        "service",
        "link",
        "url",
        "html_url",
        "permalink",
    }
    metadata = {key: value for key, value in item.items() if key not in consumed_keys and value not in ("", None, [], {})}

    return {
        "timestamp": str(timestamp),
        "type": event_type,
        "severity": severity,
        "source": source,
        "message": message,
        "tags": tags,
        "incident_id": incident_id,
        "owner": owner,
        "service": service,
        "status": status,
        "link": link,
        "metadata": metadata,
        "evidence_file": path.name,
    }


def _first_value(item: dict, *keys: str) -> Any:
    for key in keys:
        value = item.get(key)
        if value not in ("", None):
            return value
    return None


def _infer_source_from_path(path: Path) -> str:
    stem = path.stem.lower()
    for candidate in ("cloudwatch", "slack", "github-actions"):
        if candidate in stem:
            return candidate
    return stem


def _infer_type(source: str, message: str) -> str:
    source_lower = source.lower()
    message_lower = message.lower()
    if "deploy" in message_lower:
        return "deploy"
    if "rollback" in message_lower or "recover" in message_lower:
        return "recovery"
    if source_lower == "cloudwatch":
        return "alert"
    if source_lower == "slack":
        return "chatops"
    if source_lower == "github-actions":
        return "pipeline"
    return "event"


def _merge_tags(*values: Any) -> list[str]:
    tags: list[str] = []
    for value in values:
        if value in ("", None):
            continue
        if isinstance(value, list):
            for item in value:
                tags.extend(_merge_tags(item))
            continue
        if isinstance(value, dict):
            for key, inner_value in value.items():
                tags.append(f"{key}:{inner_value}")
            continue
        if isinstance(value, str):
            parts = re.split(r"[;,|]", value)
            tags.extend(part.strip() for part in parts if part.strip())
            continue
        tags.append(str(value).strip())
    return tags


def _normalize_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        cleaned = tag.strip().lower().replace(" ", "-")
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        normalized.append(cleaned)
    return normalized


def _extract_incident_id(tags: list[str]) -> str | None:
    for tag in tags:
        if tag.startswith("incident:"):
            return tag.split(":", 1)[1]
        if tag.startswith("inc-"):
            return tag
    return None


def _incident_id_from_channel(channel: str | None) -> str | None:
    if not channel:
        return None
    candidate = channel.strip().lower()
    if candidate.startswith("inc-"):
        return candidate
    return None


def _normalize_severity(value: Any) -> str:
    candidate = str(value).strip().lower()
    if candidate in SEVERITY_PRIORITY:
        return candidate
    return _severity_from_status(candidate)


def _severity_from_status(value: Any) -> str:
    candidate = str(value).strip().lower()
    if candidate in {"alarm", "critical", "fatal"}:
        return "critical"
    if candidate in {"error", "failed", "failure", "timed_out", "cancelled"}:
        return "error"
    if candidate in {"warning", "warn", "insufficient_data", "degraded"}:
        return "warning"
    if candidate in {"ok", "success", "completed", "resolved", "info"}:
        return "info"
    return _severity_from_text(candidate)


def _severity_from_text(value: str) -> str:
    lower_value = value.lower()
    if any(keyword in lower_value for keyword in ("sev-1", "critical", "outage", "customer impact")):
        return "critical"
    if any(keyword in lower_value for keyword in ("error", "failed", "5xx", "rollback")):
        return "error"
    if any(keyword in lower_value for keyword in ("warn", "degraded", "latency", "probe")):
        return "warning"
    return "info"


def _dimensions_to_map(dimensions: Any) -> dict[str, str]:
    if not isinstance(dimensions, list):
        return {}
    parsed: dict[str, str] = {}
    for item in dimensions:
        if not isinstance(item, dict):
            continue
        name = str(item.get("Name") or item.get("name") or "").strip().lower()
        value = str(item.get("Value") or item.get("value") or "").strip().lower()
        if name and value:
            parsed[name] = value
    return parsed


def _service_from_text(text: str) -> str | None:
    lowered = text.lower()
    service_match = re.search(r"([a-z0-9-]+(?:api|service|worker))", lowered)
    if service_match:
        return service_match.group(1)
    for token in re.split(r"[^a-z0-9-]+", lowered):
        if token and token not in GENERIC_SOURCE_HINTS and token not in {"prod", "main", "push", "rollback"}:
            if token in {"payments", "checkout", "catalog"}:
                return f"{token}-api"
    return None


def _service_from_tags(tags: Any) -> str | None:
    for tag in _normalize_tags(_merge_tags(tags)):
        if tag.endswith(("-api", "-service", "-worker")):
            return tag
    return None
