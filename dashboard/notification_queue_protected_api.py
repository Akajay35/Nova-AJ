from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_auth import authorize_queue_request
from dashboard.notification_queue_http_api import handle_queue_action


def handle_protected_queue_action(
    queue: NotificationQueue,
    request_path: str,
    token: str | None,
) -> tuple[int, dict]:
    """Authorize a queue-management request before executing its action."""
    if not authorize_queue_request(token):
        return 401, {"error": "unauthorized"}
    status, payload = handle_queue_action(queue, request_path)
    return status, payload
