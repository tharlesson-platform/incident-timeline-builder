from pathlib import Path

from typer.testing import CliRunner

from cli.main import app


def test_build_creates_timeline_and_postmortem(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "build",
            "--evidence-path",
            "examples/payments-incident",
            "--timezone",
            "UTC",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "timeline.json").exists()
    assert (tmp_path / "timeline.md").exists()
    assert (tmp_path / "timeline.html").exists()
    assert (tmp_path / "postmortem-draft.md").exists()
    assert "Executive summary" in (tmp_path / "postmortem-draft.md").read_text(encoding="utf-8")


def test_build_supports_recursive_directories(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "build",
            "--evidence-path",
            "examples",
            "--timezone",
            "UTC",
            "--recursive",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "incidents=" in result.stdout
