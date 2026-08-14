from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_http_api import handle_queue_action


def handle_notification_queue_request(queue: NotificationQueue, request_path: str) -> tuple[int, dict]:
    """Bridge the framework-neutral queue handler into an existing HTTP server."""
    return handle_queue_action(queue, request_path)
