from dashboard.ci_diagnostics import diagnose_ci


def test_ci_diagnostics_detects_all_required_triggers(tmp_path):
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "tests.yml").write_text(
        """name: Nova AJ tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
""",
        encoding="utf-8",
    )
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")

    result = diagnose_ci(tmp_path)

    assert result["triggers"] == {
        "push_main": True,
        "pull_request_main": True,
        "manual_dispatch": True,
    }
    assert result["ready"] is True


def test_ci_diagnostics_marks_missing_trigger_as_not_ready(tmp_path):
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "tests.yml").write_text(
        """name: Nova AJ tests
on:
  push:
    branches: [main]
  workflow_dispatch:
""",
        encoding="utf-8",
    )
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")

    result = diagnose_ci(tmp_path)

    assert result["triggers"]["push_main"] is True
    assert result["triggers"]["pull_request_main"] is False
    assert result["triggers"]["manual_dispatch"] is True
    assert result["ready"] is False
