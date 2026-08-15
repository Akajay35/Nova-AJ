from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.queue_health import queue_health


def status_payload(queue: NotificationQueue) -> dict:
    health = queue_health(queue)
    return {
        "notification_queue_health": health,
        "notification_queue_counts": {
            "total": health["total"],
            "queued": health["queued"],
            "pending": health["pending"],
            "delivered": health["delivered"],
            "failed": health["failed"],
        },
    }


def notification_queue_status(queue: NotificationQueue) -> dict:
    """Return the normalized queue health shape used by the system-health view."""
    if hasattr(queue, "status"):
        value = queue.status()
        return {
            "health": value.get("health", "unknown"),
            "counts": value.get("counts", {}),
            "total": value.get("total", 0),
        }

    health = queue_health(queue)
    return {
        "health": health["state"],
        "counts": {
            "queued": health["queued"],
            "pending": health["pending"],
            "delivered": health["delivered"],
            "failed": health["failed"],
        },
        "total": health["total"],
    }
