from __future__ import annotations

import hashlib
import time


class StartupAlertDeduplicator:
    """Deduplicate identical alerts and enforce a notification cooldown."""

    def __init__(self, cooldown_seconds: int = 300):
        self.cooldown_seconds = cooldown_seconds
        self._last_seen: dict[str, float] = {}

    @staticmethod
    def fingerprint(alert: dict) -> str:
        raw = "|".join(str(alert.get(k, "")) for k in ("severity", "title", "action", "count"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def filter(self, alerts: list[dict], now: float | None = None) -> list[dict]:
        current = time.time() if now is None else now
        result = []
        for alert in alerts:
            key = self.fingerprint(alert)
            previous = self._last_seen.get(key)
            if previous is not None and current - previous < self.cooldown_seconds:
                continue
            self._last_seen[key] = current
            enriched = dict(alert)
            enriched["fingerprint"] = key
            enriched["cooldown_seconds"] = self.cooldown_seconds
            result.append(enriched)
        return result
