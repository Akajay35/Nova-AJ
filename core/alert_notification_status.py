from __future__ import annotations

from datetime import datetime, timezone


def route_alert(alert: dict) -> dict:
    severity = str(alert.get("severity", "low"))
    routes = {
        "critical": {"channel": "urgent", "priority": "immediate"},
        "high": {"channel": "priority", "priority": "high"},
        "medium": {"channel": "standard", "priority": "normal"},
        "low": {"channel": "digest", "priority": "low"},
    }
    route = routes.get(severity, routes["low"])
    return {**alert, **route, "routed_at": datetime.now(timezone.utc).isoformat()}
