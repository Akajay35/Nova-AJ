import pytest

from core.skill_trainer import SkillTrainer
from core.tool_registry import Tool, ToolRegistry
from core.trained_skill_runtime import TrainedSkillRuntime


class Guard:
    def __init__(self, allowed=True):
        self.allowed = allowed
        self.calls = []

    def check(self, skill, permission, action=""):
        self.calls.append((skill, permission, action))
        return type("Decision", (), {"allowed": self.allowed, "reason": "blocked" if not self.allowed else "ok"})()


def test_runtime_calls_registered_tool_after_permission(tmp_path):
    trainer = SkillTrainer(tmp_path / "trained.json")
    trainer.train("report", "prepare report", "run report", ["tool:report {\"days\": 1}"], required_permissions=["reports"])
    trainer.approve("report")

    registry = ToolRegistry()
    registry.register(Tool("report", "make report", lambda days: f"report-{days}"))
    guard = Guard()

    result = TrainedSkillRuntime(trainer, registry, guard).execute("report")

    assert result == ["report-1"]
    assert guard.calls == [("trained:report", "reports", "report")]


def test_runtime_rejects_non_tool_steps(tmp_path):
    trainer = SkillTrainer(tmp_path / "trained.json")
    trainer.train("unsafe", "not executable", "unsafe", ["python:print('x')"], required_permissions=["files"])
    trainer.approve("unsafe")
    runtime = TrainedSkillRuntime(trainer, ToolRegistry(), Guard())

    with pytest.raises(ValueError, match="allowed tool action"):
        runtime.execute("unsafe")


def test_runtime_blocks_when_permission_denied(tmp_path):
    trainer = SkillTrainer(tmp_path / "trained.json")
    trainer.train("report", "prepare report", "report", ["tool:report"], required_permissions=["reports"])
    trainer.approve("report")
    registry = ToolRegistry()
    registry.register(Tool("report", "make report", lambda: "ok"))

    with pytest.raises(PermissionError, match="blocked"):
        TrainedSkillRuntime(trainer, registry, Guard(allowed=False)).execute("report")
