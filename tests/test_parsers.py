from pathlib import Path

from normalizers.timestamps import normalize_timestamp
from parsers.sources import load_sources


def test_load_sources_parses_all_supported_exports() -> None:
    events = load_sources(Path("examples/payments-incident"))
    sources = {event["source"] for event in events}
    assert {"cloudwatch", "github-actions", "slack"}.issubset(sources)
    assert any(event["incident_id"] == "payments-apr20" for event in events)


def test_normalize_timestamp_converts_timezone() -> None:
    assert normalize_timestamp("2026-04-20T10:00:00+00:00", "America/Sao_Paulo").endswith("-03:00")


def test_load_sources_parses_aws_sre_doctor_bundle() -> None:
    events = load_sources(Path("examples/aws-doctor-bundle"))
    doctor_events = [event for event in events if event["source"] == "aws-sre-doctor"]
    assert doctor_events
    assert any(event["type"] == "bundle" for event in doctor_events)
    assert any(event["type"] == "diagnosis-finding" for event in doctor_events)
