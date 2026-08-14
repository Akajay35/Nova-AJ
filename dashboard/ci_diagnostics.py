from __future__ import annotations

from pathlib import Path


def diagnose_ci(repo_root: str | Path = ".") -> dict:
    root = Path(repo_root)
    workflow = root / ".github" / "workflows" / "tests.yml"
    tests = root / "tests"
    test_files = sorted(str(p.relative_to(root)) for p in tests.rglob("test_*.py")) if tests.is_dir() else []
    return {
        "workflow_present": workflow.is_file(),
        "workflow_path": str(workflow),
        "tests_present": bool(test_files),
        "test_files": test_files,
        "test_command": "python -m pytest -q",
        "ready": workflow.is_file() and bool(test_files),
    }
