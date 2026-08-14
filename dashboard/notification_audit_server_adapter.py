from __future__ import annotations

from dashboard.notification_audit_endpoint import handle_notification_audit_request
from dashboard.notification_queue_audit import NotificationQueueAudit


def handle_audit_endpoint(
    audit: NotificationQueueAudit,
    request_path: str,
) -> tuple[int, dict]:
    """Bridge the read-only audit endpoint into an existing HTTP server."""
    return handle_notification_audit_request(audit, request_path)
