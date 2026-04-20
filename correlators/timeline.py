from __future__ import annotations

from correlators.summary import summarize
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
    summary = summarize(normalized)
    correlated = [
        item
        for item in normalized
        if probable_cause != "indeterminate"
        and any(tag in item["tags"] for tag in ["payments", "deploy", "rollback", "customer-impact"])
    ]
    return {
        "title": "Incident Timeline Builder",
        "timezone": timezone,
        "events": normalized,
        "probable_cause": probable_cause,
        "summary": summary,
        "correlated_events": correlated,
        "postmortem": {
            "summary": probable_cause,
            "impact": "Determinar impacto com base nos eventos críticos e de customer-impact",
            "follow_up_actions": [
                "Completar timeline com owners",
                "Confirmar mudança causal",
                "Definir ações corretivas e preventivas",
            ],
        },
        "next_steps": [
            "Confirmar linha do tempo com responsáveis do deploy",
            "Anexar evidências adicionais de logs e métricas",
            "Fechar rascunho de postmortem com owner e ações",
        ],
    }
