from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.queue_status_api import notification_queue_status


def notification_queue_health(queue: NotificationQueue) -> dict:
    """Return a stable JSON-ready payload for the Control Center health endpoint."""
    payload = notification_queue_status(queue)
    return {
        "service": "notification_queue",
        "status": payload.get("health", "unknown"),
        "counts": payload.get("counts", {}),
        "total": payload.get("total", 0),
    }
