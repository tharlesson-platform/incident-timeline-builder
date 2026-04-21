from __future__ import annotations

from html import escape


def render_markdown(report: dict) -> str:
    lines = [
        f"# {report['title']}",
        "",
        f"- timezone: {report['timezone']}",
        f"- generated_at: {report['generated_at']}",
        f"- primary_incident_id: {report['primary_incident_id'] or 'n/a'}",
        f"- probable_cause: {report['probable_cause']}",
        "",
        "## Summary",
        "",
        f"- total_events: {report['summary']['total_events']}",
        f"- total_incidents: {report['summary']['total_incidents']}",
        f"- counts_by_type: {report['summary']['counts_by_type']}",
        f"- counts_by_severity: {report['summary']['counts_by_severity']}",
        f"- counts_by_source: {report['summary']['counts_by_source']}",
        f"- impacted_services: {report['summary']['impacted_services']}",
        f"- timeframe: {report['summary']['timeframe']}",
        "",
        "## Confirmed facts",
        "",
    ]
    lines.extend(f"- {entry}" for entry in report["confirmed_facts"])
    lines.extend(["", "## Hypotheses", ""])
    lines.extend(f"- {entry}" for entry in report["hypotheses"])
    lines.extend([
        "",
        "## Incident groups",
        "",
    ])

    for incident in report["incidents"]:
        lines.extend(
            [
                f"### {incident['incident_id']}",
                "",
                f"- title: {incident['title']}",
                f"- severity: {incident['severity']}",
                f"- status: {incident['status']}",
                f"- services: {incident['services']}",
                f"- event_count: {incident['event_count']}",
                f"- correlation_reason: {incident['correlation_reason']}",
                f"- probable_cause: {incident['probable_cause']}",
                "",
            ]
        )

    lines.extend(["## Timeline", ""])
    for item in report["events"]:
        lines.append(
            f"- {item['timestamp']} | {item['incident_id']} | {item['severity']} | {item['source']} | {item['type']} | {item['message']}"
        )

    lines.extend(["", "## Correlated events", ""])
    for item in report["correlated_events"]:
        lines.append(f"- {item['timestamp']} | {item['severity']} | {item['message']}")

    lines.extend(["", "## 5 Whys", ""])
    lines.append(f"- method: {report['five_whys']['method']}")
    lines.append(f"- hypothesis: {report['five_whys']['hypothesis']}")
    lines.append(f"- systemic_gap: {report['five_whys']['systemic_gap']}")
    lines.append("")
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
    lines.extend(["", "## Next steps", ""])
    lines.extend(f"- {item}" for item in report["next_steps"])
    return "\n".join(lines).strip() + "\n"


def render_postmortem_markdown(report: dict) -> str:
    postmortem = report["postmortem"]
    lines = [
        f"# {postmortem['title']}",
        "",
        "## Metadata",
        "",
        f"- incident_id: {postmortem['incident_id'] or 'n/a'}",
        f"- status: {postmortem['status']}",
        f"- severity: {postmortem['severity']}",
        f"- services: {postmortem['services']}",
        f"- owners: {postmortem['owners']}",
        f"- timeframe: {postmortem['timeframe']}",
        "",
        "## Executive summary",
        "",
        postmortem["summary"],
        "",
        "## Impact",
        "",
        postmortem["impact"],
        "",
        "## Detection",
        "",
        postmortem["detection"],
        "",
        "## Root cause hypothesis",
        "",
        postmortem["root_cause_hypothesis"],
        "",
        "## Confirmed facts",
        "",
    ]
    lines.extend(f"- {entry}" for entry in postmortem["confirmed_facts"])
    lines.extend(["", "## Working hypotheses", ""])
    lines.extend(f"- {entry}" for entry in postmortem["hypotheses"])
    lines.extend([
        "",
        "## Contributing factors",
        "",
    ])
    lines.extend(f"- {entry}" for entry in postmortem["contributing_factors"])
    lines.extend(["", "## What worked", ""])
    lines.extend(f"- {entry}" for entry in postmortem["what_worked"])
    lines.extend(["", "## What failed", ""])
    lines.extend(f"- {entry}" for entry in postmortem["what_failed"])
    lines.extend(["", "## 5 Whys snapshot", ""])
    lines.append(f"- hypothesis: {postmortem['five_whys_hypothesis']}")
    lines.append(f"- systemic_gap: {postmortem['five_whys_systemic_gap']}")
    lines.extend(["", "## Follow-up actions", ""])
    for action in postmortem["follow_up_actions"]:
        lines.append(
            f"- [{action['priority']}] {action['title']} | owner={action['owner']} | status={action['status']}"
        )
    lines.extend(["", "## Evidence sources", ""])
    lines.append(f"- sources: {postmortem['evidence_sources']}")
    lines.extend(["", "## Supporting 5 Whys", ""])
    for item in report["five_whys"]["items"]:
        lines.append(f"### Why {item['index']}")
        lines.append("")
        lines.append(f"- question: {item['question']}")
        lines.append(f"- answer: {item['answer']}")
        if item["evidence"]:
            lines.append("- evidence:")
            lines.extend(f"  - {entry}" for entry in item["evidence"])
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_html(report: dict) -> str:
    summary_items = "".join(
        f"<li><strong>{escape(key)}:</strong> {escape(str(value))}</li>"
        for key, value in report["summary"].items()
        if key != "counts_by_tag"
    )
    incident_cards = "".join(
        (
            "<section class='incident-card'>"
            f"<h3>{escape(incident['incident_id'])}</h3>"
            f"<p><strong>Severity:</strong> {escape(incident['severity'])}</p>"
            f"<p><strong>Status:</strong> {escape(incident['status'])}</p>"
            f"<p><strong>Cause:</strong> {escape(incident['probable_cause'])}</p>"
            f"<p><strong>Services:</strong> {escape(', '.join(incident['services']))}</p>"
            "</section>"
        )
        for incident in report["incidents"]
    )
    timeline_rows = "".join(
        (
            "<tr>"
            f"<td>{escape(item['timestamp'])}</td>"
            f"<td>{escape(item['incident_id'] or 'n/a')}</td>"
            f"<td>{escape(item['severity'])}</td>"
            f"<td>{escape(item['source'])}</td>"
            f"<td>{escape(item['message'])}</td>"
            "</tr>"
        )
        for item in report["events"]
    )
    why_items = "".join(
        (
            "<li>"
            f"<strong>Why {item['index']}:</strong> {escape(item['question'])}<br>"
            f"{escape(item['answer'])}<br>"
            f"<em>confidence:</em> {escape(item['confidence'])}"
            "</li>"
        )
        for item in report["five_whys"]["items"]
    )
    confirmed_fact_items = "".join(f"<li>{escape(item)}</li>" for item in report["confirmed_facts"])
    hypothesis_items = "".join(f"<li>{escape(item)}</li>" for item in report["hypotheses"])
    return f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <title>{escape(report['title'])}</title>
    <style>
      body {{
        font-family: "Segoe UI", sans-serif;
        margin: 2rem auto;
        max-width: 1100px;
        color: #1f2937;
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        padding: 0 1rem 3rem;
      }}
      h1, h2, h3 {{
        color: #0f172a;
      }}
      .incident-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1rem;
      }}
      .incident-card {{
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
      }}
      th, td {{
        padding: 0.75rem;
        border-bottom: 1px solid #e5e7eb;
        text-align: left;
        vertical-align: top;
      }}
      th {{
        background: #dbeafe;
      }}
    </style>
  </head>
  <body>
    <h1>{escape(report['title'])}</h1>
    <p><strong>Timezone:</strong> {escape(report['timezone'])}</p>
    <p><strong>Primary incident:</strong> {escape(report['primary_incident_id'] or 'n/a')}</p>
    <p><strong>Probable cause:</strong> {escape(report['probable_cause'])}</p>
    <h2>Summary</h2>
    <ul>{summary_items}</ul>
    <h2>Confirmed facts</h2>
    <ul>{confirmed_fact_items}</ul>
    <h2>Hypotheses</h2>
    <ul>{hypothesis_items}</ul>
    <h2>Incident groups</h2>
    <div class="incident-grid">{incident_cards}</div>
    <h2>Timeline</h2>
    <table>
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Incident</th>
          <th>Severity</th>
          <th>Source</th>
          <th>Message</th>
        </tr>
      </thead>
      <tbody>{timeline_rows}</tbody>
    </table>
    <h2>5 Whys</h2>
    <ol>{why_items}</ol>
  </body>
</html>
"""
