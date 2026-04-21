from __future__ import annotations

from datetime import datetime, timezone

from correlators.five_whys import build_five_whys
from correlators.incidents import group_incidents, select_primary_incident
from correlators.summary import summarize
from normalizers.timestamps import normalize_timestamp
from parsers.sources import load_sources


def build_timeline(evidence_path, timezone_name: str, recursive: bool = False, title: str | None = None) -> dict:
    events = load_sources(evidence_path, recursive=recursive)
    normalized = [_normalize_event(event, timezone_name) for event in events]
    normalized = [event for event in normalized if event]
    normalized.sort(key=lambda item: item["timestamp"])

    incidents = group_incidents(normalized)
    primary_incident = select_primary_incident(incidents)
    primary_events = primary_incident["events"] if primary_incident else normalized
    probable_cause = primary_incident["probable_cause"] if primary_incident else _probable_cause_from_events(normalized)
    summary = summarize(normalized, incidents)
    five_whys = build_five_whys(primary_events, probable_cause)

    return {
        "title": title or "Incident Timeline Builder",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "timezone": timezone_name,
        "events": normalized,
        "incidents": incidents,
        "primary_incident_id": primary_incident["incident_id"] if primary_incident else None,
        "probable_cause": probable_cause,
        "summary": summary,
        "five_whys": five_whys,
        "correlated_events": _correlated_events(primary_events),
        "postmortem": _build_postmortem(primary_incident, five_whys),
        "next_steps": _next_steps(primary_incident),
    }


def _normalize_event(event: dict, timezone_name: str) -> dict:
    tags = event.get("tags", [])
    if isinstance(tags, str):
        tags = [item for item in tags.split(";") if item]

    normalized_tags: list[str] = []
    seen_tags: set[str] = set()
    for tag in tags:
        cleaned = str(tag).strip().lower()
        if cleaned and cleaned not in seen_tags:
            seen_tags.add(cleaned)
            normalized_tags.append(cleaned)

    return {
        "timestamp": normalize_timestamp(str(event["timestamp"]), timezone_name),
        "type": str(event.get("type", "unknown")).strip().lower() or "unknown",
        "severity": str(event.get("severity", "info")).strip().lower() or "info",
        "source": str(event.get("source", "unknown")).strip().lower() or "unknown",
        "message": str(event.get("message", "")).strip(),
        "tags": normalized_tags,
        "incident_id": event.get("incident_id"),
        "owner": event.get("owner"),
        "service": event.get("service"),
        "status": event.get("status"),
        "link": event.get("link"),
        "metadata": event.get("metadata", {}),
        "evidence_file": event.get("evidence_file"),
    }


def _probable_cause_from_events(events: list[dict]) -> str:
    return next((item["message"] for item in events if item["severity"] in {"critical", "error"}), "indeterminate")


def _correlated_events(events: list[dict]) -> list[dict]:
    if not events:
        return []
    return [
        item
        for item in events
        if item["severity"] in {"critical", "error"}
        or any(tag in item["tags"] for tag in ("deploy", "rollback", "customer-impact", "probe"))
    ]


def _build_postmortem(primary_incident: dict | None, five_whys: dict) -> dict:
    if not primary_incident:
        return {
            "title": "Postmortem draft",
            "incident_id": None,
            "status": "draft",
            "severity": "unknown",
            "services": [],
            "owners": ["TBD"],
            "summary": "Sem dados suficientes para montar um postmortem consistente.",
            "impact": "Completar a coleta de evidencias antes de fechar o impacto.",
            "timeframe": {},
            "detection": "Sem incidente principal identificado.",
            "root_cause_hypothesis": five_whys["hypothesis"],
            "contributing_factors": ["Completar coleta de evidencia adicional"],
            "what_worked": ["A consolidacao local ja gera a primeira timeline"],
            "what_failed": ["Ainda faltam eventos suficientes para RCA"],
            "five_whys_hypothesis": five_whys["hypothesis"],
            "five_whys_systemic_gap": five_whys["systemic_gap"],
            "follow_up_actions": _follow_up_actions(services=[]),
            "evidence_sources": {},
        }

    impact_events = [event for event in primary_incident["events"] if "customer-impact" in event.get("tags", [])]
    detection_event = next(
        (
            event
            for event in primary_incident["events"]
            if event["severity"] in {"critical", "error"} or event["type"] in {"alert", "validation"}
        ),
        None,
    )

    services = primary_incident["services"]
    return {
        "title": f"Postmortem draft - {primary_incident['incident_id']}",
        "incident_id": primary_incident["incident_id"],
        "status": primary_incident["status"],
        "severity": primary_incident["severity"],
        "services": services,
        "owners": primary_incident["owners"] or ["TBD"],
        "summary": primary_incident["probable_cause"],
        "impact": _impact_summary(primary_incident, impact_events),
        "timeframe": {
            "start": primary_incident["start"],
            "end": primary_incident["end"],
            "duration_minutes": primary_incident["duration_minutes"],
        },
        "detection": detection_event["message"] if detection_event else "Definir mecanismo inicial de deteccao.",
        "root_cause_hypothesis": primary_incident["probable_cause"],
        "contributing_factors": _contributing_factors(primary_incident),
        "what_worked": _what_worked(primary_incident),
        "what_failed": _what_failed(primary_incident),
        "five_whys_hypothesis": five_whys["hypothesis"],
        "five_whys_systemic_gap": five_whys["systemic_gap"],
        "follow_up_actions": _follow_up_actions(services),
        "evidence_sources": _count_by_key(primary_incident["events"], "source"),
    }


def _impact_summary(primary_incident: dict, impact_events: list[dict]) -> str:
    services = ", ".join(primary_incident["services"]) or "servico nao identificado"
    if impact_events:
        return (
            f"Foram observados {len(impact_events)} eventos de impacto ao cliente para {services} "
            f"durante {primary_incident['duration_minutes']} minutos."
        )
    return f"O incidente afetou {services}, mas ainda precisa de confirmacao detalhada do impacto ao cliente."


def _contributing_factors(primary_incident: dict) -> list[str]:
    factors: list[str] = []
    if any(event["type"] == "deploy" for event in primary_incident["events"]):
        factors.append("Mudanca de deploy proxima ao inicio da degradacao")
    if any(event["type"] == "infra" for event in primary_incident["events"]):
        factors.append("Mudanca de infraestrutura na mesma janela do incidente")
    if not any(event["type"] == "validation" for event in primary_incident["events"]):
        factors.append("Ausencia de validacao clara antes do impacto")
    if not factors:
        factors.append("Complementar fatores contribuintes com logs e metricas")
    return factors


def _what_worked(primary_incident: dict) -> list[str]:
    worked: list[str] = []
    if any("rollback" in event.get("tags", []) for event in primary_incident["events"]):
        worked.append("Rollback ou mitigacao foi registrado na timeline")
    if any(event["source"] == "slack" for event in primary_incident["events"]):
        worked.append("Comunicacao operacional ficou preservada em evidencias de ChatOps")
    if not worked:
        worked.append("A timeline consolidou evidencias suficientes para iniciar a RCA")
    return worked


def _what_failed(primary_incident: dict) -> list[str]:
    failed: list[str] = []
    if any(event["severity"] in {"critical", "error"} for event in primary_incident["events"]):
        failed.append("O problema chegou ao cliente antes de ser bloqueado automaticamente")
    if not any(event["source"] == "cloudwatch" for event in primary_incident["events"]):
        failed.append("Nao ha alarme de monitoramento anexado ao incidente principal")
    if not any(event["source"] == "github-actions" for event in primary_incident["events"]):
        failed.append("Nao ha evidencia de pipeline/deploy anexada ao incidente principal")
    return failed or ["Completar o que falhou com evidencias adicionais"]


def _follow_up_actions(services: list[str]) -> list[dict]:
    service_label = ", ".join(services) if services else "servico impactado"
    return [
        {
            "title": f"Adicionar guardrail pre-deploy para {service_label}",
            "owner": "TBD",
            "priority": "high",
            "status": "open",
        },
        {
            "title": "Confirmar causa raiz com owners de aplicacao e plataforma",
            "owner": "TBD",
            "priority": "high",
            "status": "open",
        },
        {
            "title": "Transformar o gap sistemico em acao corretiva com prazo",
            "owner": "TBD",
            "priority": "medium",
            "status": "open",
        },
    ]


def _count_by_key(events: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        value = event.get(key)
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def _next_steps(primary_incident: dict | None) -> list[str]:
    if not primary_incident:
        return [
            "Adicionar mais evidencias para identificar um incidente principal",
            "Executar novamente o build com exportacoes de monitoramento, chat e pipelines",
        ]
    return [
        f"Validar o incidente {primary_incident['incident_id']} com owners e on-call",
        "Anexar logs, metricas e links de mudanças relevantes na mesma janela",
        "Fechar o postmortem com RCA confirmada, impacto e acoes preventivas",
        "Priorizar os follow-ups que eliminam a dependencia de mitigacao reativa",
    ]
