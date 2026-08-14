from __future__ import annotations

from pathlib import Path


def diagnose_ci(repo_root: str | Path = ".") -> dict:
    root = Path(repo_root)
    workflow = root / ".github" / "workflows" / "tests.yml"
    tests = root / "tests"
    test_files = sorted(str(p.relative_to(root)) for p in tests.rglob("test_*.py")) if tests.is_dir() else []
    workflow_text = workflow.read_text(encoding="utf-8") if workflow.is_file() else ""
    push_main = "push:" in workflow_text and "branches: [main]" in workflow_text
    pull_request_main = "pull_request:" in workflow_text and "branches: [main]" in workflow_text
    manual = "workflow_dispatch:" in workflow_text
    return {
        "workflow_present": workflow.is_file(),
        "workflow_path": str(workflow),
        "tests_present": bool(test_files),
        "test_files": test_files,
        "test_command": "python -m pytest -q",
        "triggers": {
            "push_main": push_main,
            "pull_request_main": pull_request_main,
            "manual_dispatch": manual,
        },
        "ready": workflow.is_file() and bool(test_files) and push_main and pull_request_main and manual,
    }
