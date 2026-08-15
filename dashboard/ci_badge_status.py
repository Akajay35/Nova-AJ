from __future__ import annotations

from urllib.parse import urlparse


def ci_badge_status(workflow_url: str | None = None) -> dict:
    """Return safe metadata for displaying the GitHub Actions workflow status."""
    if workflow_url:
        parsed = urlparse(workflow_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return {"status": "unknown", "workflow_url": None}
    return {
        "status": "unknown",
        "workflow_url": workflow_url,
        "source": "github-actions",
        "message": "No workflow run has been reported yet.",
    }
