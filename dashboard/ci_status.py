from __future__ import annotations

from pathlib import Path


def ci_configuration_status(repo_root: str | Path = ".") -> dict:
    """Report whether the Nova AJ test workflow is present on disk."""
    workflow = Path(repo_root) / ".github" / "workflows" / "tests.yml"
    return {
        "workflow": str(workflow),
        "present": workflow.is_file(),
        "status": "configured" if workflow.is_file() else "missing",
    }
