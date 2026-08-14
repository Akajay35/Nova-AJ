from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.system_health_view import system_health_snapshot
from dashboard.notification_queue_audit import NotificationQueueAudit


def handle_system_health_request(
    queue: NotificationQueue,
    audit: NotificationQueueAudit,
    request_path: str,
    repo_root: str = ".",
) -> tuple[int, dict]:
    """Serve a read-only JSON system-health endpoint."""
    from urllib.parse import urlparse

    parsed = urlparse(request_path)
    if parsed.path != "/api/system-health":
        return 404, {"error": "not found"}
    return 200, system_health_snapshot(queue, audit, repo_root)
