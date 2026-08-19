from __future__ import annotations

from core.permission_guard import PermissionGuard
from core.permission_manager import PermissionManager
from core.skill_trainer import SkillTrainer
from core.tool_registry import Tool, ToolRegistry
from core.trained_skill_runtime import TrainedSkillRuntime


def test_training_approval_and_execution(tmp_path):
    trainer = SkillTrainer(storage_path=tmp_path / "trained_skills.json")
    trainer.train(
        name="report",
        trigger="run report",
        steps=["tool:calculate {\"expression\": \"2+2\"}"],
        required_permissions=["calculator"],
        risk_level="low",
    )
    trainer.approve("report")

    permissions = PermissionManager(config_path=tmp_path / "permissions.json")
    permissions.grant("trained:report", "calculator")
    guard = PermissionGuard(permissions)

    tools = ToolRegistry()
    tools.register(Tool(name="calculate", description="test calculator", handler=lambda expression: str(eval(expression, {"__builtins__": {}}, {}))))
    runtime = TrainedSkillRuntime(trainer, tools, guard)

    assert runtime.execute("report") == ["4"]


def test_unapproved_skill_cannot_execute(tmp_path):
    trainer = SkillTrainer(storage_path=tmp_path / "trained_skills.json")
    trainer.train(name="draft", trigger="run draft", steps=["tool:calculate {\"expression\": \"2+2\"}"], required_permissions=["calculator"], risk_level="low")
    permissions = PermissionManager(config_path=tmp_path / "permissions.json")
    guard = PermissionGuard(permissions)
    tools = ToolRegistry()
    tools.register(Tool(name="calculate", description="test", handler=lambda expression: "4"))
    runtime = TrainedSkillRuntime(trainer, tools, guard)

    try:
        runtime.execute("draft")
        assert False, "inactive trained skill must be blocked"
    except PermissionError:
        pass
