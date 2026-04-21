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
