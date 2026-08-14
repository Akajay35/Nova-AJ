from __future__ import annotations

import json
from pathlib import Path

DEFAULT_COOLDOWN_SECONDS = 300


def load_cooldown(path: str | Path, default: int = DEFAULT_COOLDOWN_SECONDS) -> int:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8")).get("cooldown_seconds", default)
        return max(0, int(value))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return default


def save_cooldown(path: str | Path, seconds: int) -> int:
    seconds = max(0, int(seconds))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"cooldown_seconds": seconds}, indent=2) + "\n", encoding="utf-8")
    return seconds
