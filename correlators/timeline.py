from __future__ import annotations

from parsers.sources import load_sources
from normalizers.timestamps import normalize_timestamp


def build_timeline(evidence_path, timezone: str) -> dict:
    events = load_sources(evidence_path)
    normalized = []
    for event in events:
        tags = event.get("tags", [])
        if isinstance(tags, str):
            tags = [item for item in tags.split(";") if item]
        normalized.append(
            {
                "timestamp": normalize_timestamp(event["timestamp"]),
                "type": event.get("type", "unknown"),
                "severity": event.get("severity", "info"),
                "source": event.get("source", "unknown"),
                "message": event.get("message", ""),
                "tags": tags,
            }
        )
    normalized.sort(key=lambda item: item["timestamp"])
    probable_cause = next((item["message"] for item in normalized if item["severity"] in {"critical", "error"}), "indeterminate")
    return {
        "title": "Incident Timeline Builder",
        "timezone": timezone,
        "events": normalized,
        "probable_cause": probable_cause,
        "next_steps": [
            "Confirmar linha do tempo com responsáveis do deploy",
            "Anexar evidências adicionais de logs e métricas",
            "Fechar rascunho de postmortem com owner e ações",
        ],
    }
