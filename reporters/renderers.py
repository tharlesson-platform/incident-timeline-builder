from __future__ import annotations


def render_markdown(report: dict) -> str:
    lines = ["# Incident Timeline Builder", "", f"- probable_cause: {report['probable_cause']}", "", "## Timeline", ""]
    lines.extend(f"- {item['timestamp']} | {item['severity']} | {item['type']} | {item['message']}" for item in report["events"])
    lines.extend(["", "## Summary", ""])
    lines.append(f"- counts_by_type: {report['summary']['counts_by_type']}")
    lines.append(f"- counts_by_severity: {report['summary']['counts_by_severity']}")
    lines.extend(["", "## 5 Whys", ""])
    lines.append(f"- method: {report['five_whys']['method']}")
    lines.append(f"- hypothesis: {report['five_whys']['hypothesis']}")
    lines.append(f"- systemic_gap: {report['five_whys']['systemic_gap']}")
    lines.extend([""])
    for item in report["five_whys"]["items"]:
        lines.append(f"### Why {item['index']}")
        lines.append("")
        lines.append(f"- question: {item['question']}")
        lines.append(f"- answer: {item['answer']}")
        lines.append(f"- confidence: {item['confidence']}")
        if item["evidence"]:
            lines.append("- evidence:")
            lines.extend(f"  - {entry}" for entry in item["evidence"])
        lines.append("")
    lines.append("### Recommended actions")
    lines.append("")
    lines.extend(f"- {entry}" for entry in report["five_whys"]["recommended_actions"])
    lines.extend(["", "## Postmortem draft", ""])
    lines.append(f"- summary: {report['postmortem']['summary']}")
    lines.append(f"- impact: {report['postmortem']['impact']}")
    lines.append(f"- five_whys_hypothesis: {report['postmortem']['five_whys_hypothesis']}")
    lines.append(f"- five_whys_systemic_gap: {report['postmortem']['five_whys_systemic_gap']}")
    lines.extend(["", "## Próximos passos", ""])
    lines.extend(f"- {item}" for item in report["next_steps"])
    return "\n".join(lines).strip() + "\n"


def render_html(report: dict) -> str:
    rows = "".join(f"<li>{item['timestamp']} - {item['message']}</li>" for item in report["events"])
    whys = "".join(
        (
            "<li>"
            f"<strong>Why {item['index']}:</strong> {item['question']}<br>"
            f"{item['answer']}<br>"
            f"<em>confidence:</em> {item['confidence']}"
            "</li>"
        )
        for item in report["five_whys"]["items"]
    )
    return (
        "<!doctype html><html lang='pt-BR'><body>"
        "<h1>Incident Timeline Builder</h1>"
        "<h2>Timeline</h2>"
        f"<ul>{rows}</ul>"
        "<h2>5 Whys</h2>"
        f"<p><strong>Hypothesis:</strong> {report['five_whys']['hypothesis']}</p>"
        f"<p><strong>Systemic gap:</strong> {report['five_whys']['systemic_gap']}</p>"
        f"<ol>{whys}</ol>"
        "</body></html>"
    )
