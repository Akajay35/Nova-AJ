from __future__ import annotations


def build_alerts(health: dict) -> list[dict]:
    counts = health.get("counts", {})
    alerts = []
    if counts.get("critical", 0):
        alerts.append({"severity": "critical", "title": "Critical startup issue", "count": counts["critical"], "action": "Investigate immediately."})
    if counts.get("high", 0):
        alerts.append({"severity": "high", "title": "High-priority startup issue", "count": counts["high"], "action": "Review before normal operation."})
    if not alerts:
        alerts.append({"severity": "info", "title": "No urgent startup alerts", "count": 0, "action": "Startup health is within normal limits."})
    return alerts
