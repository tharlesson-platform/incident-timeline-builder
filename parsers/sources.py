from __future__ import annotations

import csv
import json
from pathlib import Path


def load_sources(directory: Path) -> list[dict]:
    events = []
    for path in directory.iterdir():
        if path.suffix.lower() == ".csv":
            with path.open(encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                events.extend(dict(item) for item in reader)
        elif path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                events.extend(payload)
    return events
