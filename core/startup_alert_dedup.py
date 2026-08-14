from __future__ import annotations

import hashlib
import time


class StartupAlertDeduplicator:
    """Deduplicate identical alerts using severity-specific cooldowns."""

    def __init__(self, cooldown_seconds: int = 300, cooldowns: dict[str, int] | None = None):
        self.cooldown_seconds = cooldown_seconds
        self.cooldowns = cooldowns or {}
        self._last_seen: dict[str, float] = {}

    @staticmethod
    def fingerprint(alert: dict) -> str:
        raw = "|".join(str(alert.get(k, "")) for k in ("severity", "title", "action", "count"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def cooldown_for(self, alert: dict) -> int:
        return max(0, int(self.cooldowns.get(str(alert.get("severity", "")), self.cooldown_seconds)))

    def filter(self, alerts: list[dict], now: float | None = None) -> list[dict]:
        current = time.time() if now is None else now
        result = []
        for alert in alerts:
            key = self.fingerprint(alert)
            cooldown = self.cooldown_for(alert)
            previous = self._last_seen.get(key)
            if previous is not None and current - previous < cooldown:
                continue
            self._last_seen[key] = current
            enriched = dict(alert)
            enriched["fingerprint"] = key
            enriched["cooldown_seconds"] = cooldown
            result.append(enriched)
        return result
