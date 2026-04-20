from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from correlators.timeline import build_timeline
from reporters.renderers import render_html, render_markdown


app = typer.Typer(help="Build incident timelines and postmortem drafts from local evidence.")
console = Console()


def run() -> None:
    app()


@app.command()
def version() -> None:
    console.print("0.1.0")


@app.command()
def build(
    evidence_path: Path = typer.Option(..., exists=True),
    timezone: str = typer.Option("UTC"),
    output_dir: Path = typer.Option(Path("artifacts")),
) -> None:
                report = build_timeline(evidence_path, timezone)
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / "timeline.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                (output_dir / "timeline.md").write_text(render_markdown(report), encoding="utf-8")
                (output_dir / "timeline.html").write_text(render_html(report), encoding="utf-8")
                (output_dir / "postmortem-draft.md").write_text(render_markdown(report), encoding="utf-8")
                console.print(f"events={len(report['events'])} probable_cause={report['probable_cause']}")
