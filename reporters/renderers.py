from __future__ import annotations


def render_markdown(report: dict) -> str:
    lines = ["# Incident Timeline Builder", "", f"- probable_cause: {report['probable_cause']}", "", "## Timeline", ""]
    lines.extend(f"- {item['timestamp']} | {item['severity']} | {item['type']} | {item['message']}" for item in report["events"])
    lines.extend(["", "## Próximos passos", ""])
    lines.extend(f"- {item}" for item in report["next_steps"])
    return "\n".join(lines).strip() + "\n"


def render_html(report: dict) -> str:
    rows = "".join(f"<li>{item['timestamp']} - {item['message']}</li>" for item in report["events"])
    return f"""<!doctype html><html lang='pt-BR'><body><h1>Incident Timeline Builder</h1><ul>{rows}</ul></body></html>"""
