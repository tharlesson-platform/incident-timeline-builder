from pathlib import Path

from correlators.timeline import build_timeline


def test_build_timeline_includes_incident_groups_and_postmortem() -> None:
    report = build_timeline(Path("examples/payments-incident"), "UTC")
    assert report["summary"]["counts_by_source"]["cloudwatch"] >= 1
    assert report["summary"]["counts_by_source"]["github-actions"] >= 1
    assert report["summary"]["counts_by_source"]["slack"] >= 1
    assert report["incidents"]
    assert report["primary_incident_id"] == "payments-apr20"
    assert report["postmortem"]["follow_up_actions"]
    assert report["five_whys"]["method"] == "Google-style 5 Whys"
    assert len(report["five_whys"]["items"]) == 5
    assert report["postmortem"]["five_whys_systemic_gap"]


def test_build_timeline_groups_multiple_incidents() -> None:
    report = build_timeline(Path("examples/multi-incident"), "UTC")
    assert len(report["incidents"]) >= 2
    assert report["summary"]["total_incidents"] >= 2
    assert report["primary_incident_id"]
