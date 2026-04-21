from __future__ import annotations

from datetime import datetime


CHANGE_TYPES = {"deploy", "infra", "pipeline"}
VALIDATION_KEYWORDS = ("health", "check", "probe", "canary", "validate", "validation")
RECOVERY_KEYWORDS = ("rollback", "revert", "recover", "mitigation", "failover")


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _find_trigger_event(events: list[dict]) -> dict | None:
    for event in events:
        if "customer-impact" in event.get("tags", []) and event.get("severity") in {"critical", "error"}:
            return event
    for event in events:
        if event.get("severity") in {"critical", "error"}:
            return event
    return events[0] if events else None


def _find_nearest_change_event(events: list[dict], trigger: dict | None) -> dict | None:
    if not trigger:
        return None
    trigger_time = _parse_timestamp(trigger["timestamp"])
    candidates = []
    for event in events:
        if event is trigger:
            continue
        tags = event.get("tags", [])
        is_change = event.get("type") in CHANGE_TYPES or any(tag in {"deploy", "rollback"} for tag in tags)
        if not is_change:
            continue
        delta = abs((_parse_timestamp(event["timestamp"]) - trigger_time).total_seconds())
        candidates.append((delta, event))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def _find_recovery_event(events: list[dict], trigger: dict | None) -> dict | None:
    if not trigger:
        return None
    trigger_time = _parse_timestamp(trigger["timestamp"])
    for event in events:
        if _parse_timestamp(event["timestamp"]) < trigger_time:
            continue
        message = event.get("message", "").lower()
        tags = [tag.lower() for tag in event.get("tags", [])]
        if any(keyword in message for keyword in RECOVERY_KEYWORDS) or any(keyword in tags for keyword in RECOVERY_KEYWORDS):
            return event
    return None


def _has_pre_impact_validation(events: list[dict], trigger: dict | None) -> bool:
    if not trigger:
        return False
    trigger_time = _parse_timestamp(trigger["timestamp"])
    for event in events:
        if _parse_timestamp(event["timestamp"]) >= trigger_time:
            continue
        message = event.get("message", "").lower()
        if any(keyword in message for keyword in VALIDATION_KEYWORDS):
            return True
    return False


def _evidence_lines(*events: dict | None) -> list[str]:
    lines: list[str] = []
    for event in events:
        if not event:
            continue
        lines.append(f"{event['timestamp']} | {event['source']} | {event['type']} | {event['message']}")
    return lines


def _impact_answer(trigger: dict | None) -> tuple[str, str, list[str]]:
    if not trigger:
        return (
            "Por que houve impacto?",
            "Porque a timeline ainda nao possui um evento de gatilho suficientemente claro para explicar o impacto.",
            [],
        )
    return (
        "Por que os usuarios sentiram impacto?",
        (
            f"Porque as evidencias mostram um evento de severidade {trigger['severity']} em {trigger['source']}: "
            f"'{trigger['message']}'. Esse e o primeiro sinal forte de degradacao visivel."
        ),
        _evidence_lines(trigger),
    )


def _trigger_answer(trigger: dict | None, change_event: dict | None) -> tuple[str, str, list[str]]:
    if change_event:
        return (
            "Por que a degradacao comecou naquele momento?",
            (
                f"Porque a mudanca ou evidencia tecnica mais proxima do impacto foi '{change_event['message']}' "
                f"({change_event['type']} via {change_event['source']}). Ela e a melhor candidata a gatilho inicial."
            ),
            _evidence_lines(change_event, trigger),
        )
    return (
        "Por que a degradacao comecou naquele momento?",
        "Porque ainda nao existe uma mudanca tecnica anterior bem delimitada na timeline; precisamos de mais evidencias de deploy ou infraestrutura.",
        _evidence_lines(trigger),
    )


def _system_answer(trigger: dict | None, change_event: dict | None) -> tuple[str, str, list[str]]:
    if change_event and "listener" in change_event.get("message", "").lower():
        answer = "Porque uma alteracao no caminho de trafego parece ter chegado ao ambiente sem evidencia de validacao suficiente do listener ou target group."
    elif change_event and change_event.get("type") == "deploy":
        answer = "Porque um deploy proximo ao impacto provavelmente introduziu um estado nao saudavel antes da estabilizacao do workload."
    elif trigger and "5xx" in trigger.get("message", "").lower():
        answer = "Porque a plataforma nao absorveu a falha antes que ela se manifestasse como erro de requisicao para o usuario."
    else:
        answer = "Porque nao aparece uma barreira clara entre o evento tecnico e o impacto ao cliente, o que sugere falta de protecao ou validacao suficiente."
    return (
        "Por que isso virou impacto visivel ao cliente?",
        answer,
        _evidence_lines(change_event, trigger),
    )


def _detection_answer(events: list[dict], trigger: dict | None) -> tuple[str, str, list[str]]:
    if not trigger:
        return (
            "Por que nao detectamos antes?",
            "Porque a timeline ainda esta incompleta para avaliar deteccao e validacao preventiva.",
            [],
        )
    trigger_time = _parse_timestamp(trigger["timestamp"])
    pre_impact_signals = [
        event
        for event in events
        if _parse_timestamp(event["timestamp"]) < trigger_time and event.get("severity") in {"warning", "error", "critical"}
    ]
    has_validation = _has_pre_impact_validation(events, trigger)
    if not pre_impact_signals and not has_validation:
        answer = "Porque nao existe na timeline nenhuma validacao bem-sucedida nem alerta preventivo antes do evento de customer-impact."
    elif pre_impact_signals and not has_validation:
        answer = "Porque havia sinais anteriores, mas nao aparece nenhuma validacao ou gate que tenha interrompido a mudanca antes do impacto."
    else:
        answer = "Porque mesmo com sinais ou validacoes anteriores, a timeline indica que eles nao foram suficientes para bloquear a regressao."
    return (
        "Por que isso nao foi bloqueado ou percebido antes do impacto?",
        answer,
        _evidence_lines(*(pre_impact_signals[-2:] + [trigger])),
    )


def _recovery_answer(trigger: dict | None, recovery_event: dict | None) -> tuple[str, str, list[str]]:
    if recovery_event:
        return (
            "Por que a recuperacao dependeu de acao reativa?",
            (
                f"Porque a primeira evidencia clara de mitigacao foi '{recovery_event['message']}'. "
                "Isso sugere rollback ou intervencao reativa, e nao uma protecao automatica anterior ao impacto."
            ),
            _evidence_lines(trigger, recovery_event),
        )
    return (
        "Por que o sistema ainda ficou fragil para recuperacao?",
        "Porque a timeline nao mostra uma mitigacao explicita; isso aponta para uma lacuna de automacao, rollback ou captura de evidencias de recovery.",
        _evidence_lines(trigger),
    )


def build_five_whys(events: list[dict], probable_cause: str) -> dict:
    trigger = _find_trigger_event(events)
    change_event = _find_nearest_change_event(events, trigger)
    recovery_event = _find_recovery_event(events, trigger)

    entries = []
    for index, builder in enumerate(
        (
            lambda: _impact_answer(trigger),
            lambda: _trigger_answer(trigger, change_event),
            lambda: _system_answer(trigger, change_event),
            lambda: _detection_answer(events, trigger),
            lambda: _recovery_answer(trigger, recovery_event),
        ),
        start=1,
    ):
        question, answer, evidence = builder()
        entries.append(
            {
                "index": index,
                "question": question,
                "answer": answer,
                "evidence": evidence,
                "confidence": "medium" if evidence else "low",
            }
        )

    if change_event and recovery_event:
        systemic_gap = "Fortalecer guardrails de mudanca, validacao pre-impacto e rollback automatizado para alteracoes proximas ao trafego do cliente."
    elif change_event:
        systemic_gap = "Melhorar validacao e bloqueios em mudancas para reduzir a chance de degradacao visivel."
    else:
        systemic_gap = "Melhorar captura de evidencias de mudanca e recovery para suportar RCA mais precisa."

    return {
        "method": "Google-style 5 Whys",
        "hypothesis": probable_cause,
        "items": entries,
        "systemic_gap": systemic_gap,
        "recommended_actions": [
            "Validar a linha do tempo com owner de deploy e infraestrutura",
            "Confirmar se o evento tecnico candidato realmente precedeu o impacto",
            "Transformar o gap sistemico em acao corretiva com dono e prazo",
        ],
    }
