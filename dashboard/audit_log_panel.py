from __future__ import annotations

from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.notification_queue_audit_api import audit_snapshot


def render_audit_log_panel(audit: NotificationQueueAudit, limit: int = 50) -> str:
    """Render a framework-neutral, read-only HTML audit panel."""
    payload = audit_snapshot(audit, limit)
    rows = []
    for event in reversed(payload["events"]):
        state = "success" if event.get("success") else "failed"
        rows.append(
            "<div class='audit-row'>"
            f"<b class='audit-{state}'>{state.upper()}</b> "
            f"<span>{_esc(event.get('action'))}</span> · "
            f"<span>{_esc(event.get('item_id'))}</span> · "
            f"<span>{_esc(event.get('actor'))}</span>"
            f"<div class='audit-meta'>{_esc(event.get('timestamp'))}"
            f"{(' · ' + _esc(event.get('reason'))) if event.get('reason') else ''}</div>"
            "</div>"
        )
    return (
        "<section class='card audit-panel'><b>🔐 Security Audit Log</b>"
        f"<div class='audit-total'>Total events: {payload['total']}</div>"
        + ("".join(rows) if rows else "<div class='muted'>No security events recorded.</div>")
        + "</section>"
    )


def _esc(value: object) -> str:
    text = str(value if value is not None else "")
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))
