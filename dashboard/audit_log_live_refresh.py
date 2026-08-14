from __future__ import annotations

from dashboard.audit_log_control_center_adapter import render_security_audit_section
from dashboard.notification_queue_audit import NotificationQueueAudit


DEFAULT_REFRESH_MS = 5000


def live_audit_panel(audit: NotificationQueueAudit, limit: int = 50, refresh_ms: int = DEFAULT_REFRESH_MS) -> str:
    """Render a read-only audit panel that refreshes itself from a local endpoint."""
    refresh_ms = max(1000, min(60000, int(refresh_ms)))
    panel = render_security_audit_section(audit, limit)
    script = (
        "<script>(function(){"
        "const root=document.querySelector('.audit-panel');"
        "if(!root)return;"
        "async function refresh(){try{const r=await fetch('/api/notification-audit?limit="
        + str(max(1, min(200, int(limit))))
        + "',{cache:'no-store'});if(!r.ok)return;const d=await r.json();"
        "if(d.html){root.outerHTML=d.html;}}catch(_){}}"
        "setInterval(refresh," + str(refresh_ms) + ");"
        "})();</script>"
    )
    return panel + script
