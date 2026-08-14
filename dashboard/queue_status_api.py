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
