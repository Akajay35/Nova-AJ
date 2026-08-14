from __future__ import annotations

from html import escape
from pathlib import Path

from dashboard.ci_status import ci_configuration_status


def render_ci_status_panel(repo_root: str | Path = ".") -> str:
    """Render a small read-only CI configuration panel for the Control Center."""
    status = ci_configuration_status(repo_root)
    state = escape(status["status"])
    workflow = escape(status["workflow"])
    return (
        '<section class="ci-status-panel" aria-label="CI status">'
        '<h3>Automated Tests</h3>'
        f'<p>Status: <strong>{state}</strong></p>'
        f'<p>Workflow: <code>{workflow}</code></p>'
        '</section>'
    )
