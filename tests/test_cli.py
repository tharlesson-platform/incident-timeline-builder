from pathlib import Path

from typer.testing import CliRunner

from cli.main import app


def test_build_creates_timeline() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["build", "--evidence-path", "examples"])
    assert result.exit_code == 0, result.stdout
    assert Path("artifacts/timeline.json").exists()
    assert Path("artifacts/postmortem-draft.md").exists()
    assert "5 Whys" in Path("artifacts/postmortem-draft.md").read_text(encoding="utf-8")
