from pathlib import Path

from correlators.timeline import build_timeline


def test_build_timeline_includes_postmortem() -> None:
    report = build_timeline(Path("examples"), "UTC")
    assert report["summary"]["counts_by_type"]
    assert report["postmortem"]["follow_up_actions"]
