from __future__ import annotations

from dashboard.audit_log_panel import render_audit_log_panel
from dashboard.notification_queue_audit import NotificationQueueAudit


def render_security_audit_section(audit: NotificationQueueAudit, limit: int = 50) -> str:
    """Return the audit section for embedding in an existing Control Center page."""
    return render_audit_log_panel(audit, max(1, min(200, int(limit))))
