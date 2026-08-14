from __future__ import annotations

import json
from pathlib import Path

DEFAULTS = {"critical": 60, "high": 300, "medium": 900, "low": 1800}


def load(path: str | Path) -> dict[str, int]:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return {k: max(0, int(raw.get(k, v))) for k, v in DEFAULTS.items()}
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULTS.copy()


def save(path: str | Path, values: dict[str, int]) -> dict[str, int]:
    result = {k: max(0, int(values.get(k, DEFAULTS[k]))) for k in DEFAULTS}
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
