from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationRoute:
    severity: str
    channel: str
    priority: str


DEFAULT_ROUTES = {
    "critical": NotificationRoute("critical", "urgent", "immediate"),
    "high": NotificationRoute("high", "priority", "high"),
    "medium": NotificationRoute("medium", "standard", "normal"),
    "low": NotificationRoute("low", "digest", "low"),
}


def route_alert(alert: dict, routes: dict[str, NotificationRoute] | None = None) -> dict:
    routes = routes or DEFAULT_ROUTES
    severity = str(alert.get("severity", "low")).lower()
    route = routes.get(severity, routes["low"])
    result = dict(alert)
    result["notification"] = {
        "channel": route.channel,
        "priority": route.priority,
    }
    return result


def route_alerts(alerts: list[dict], routes: dict[str, NotificationRoute] | None = None) -> list[dict]:
    return [route_alert(alert, routes) for alert in alerts]
