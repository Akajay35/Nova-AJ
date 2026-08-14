from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.system_health_endpoint import handle_system_health_request


def handle_system_health_endpoint(
    queue: NotificationQueue,
    audit: NotificationQueueAudit,
    request_path: str,
    repo_root: str = ".",
) -> tuple[int, dict]:
    """Bridge the read-only system-health endpoint into an existing HTTP server."""
    return handle_system_health_request(queue, audit, request_path, repo_root)
