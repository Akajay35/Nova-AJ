from core.tool_intelligence import ToolIntelligence
from core.tool_registry import Tool, ToolRegistry


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(Tool("train_skill", "Create a user-trained skill draft", lambda **kwargs: kwargs, risk_level="medium"))
    registry.register(Tool("test_trained_skill", "Test a trained skill trigger", lambda **kwargs: kwargs))
    registry.register(Tool("approve_trained_skill", "Activate a trained skill", lambda **kwargs: kwargs, risk_level="medium"))
    registry.register(Tool("disable_trained_skill", "Disable a trained skill", lambda **kwargs: kwargs, risk_level="medium"))
    registry.register(Tool("list_trained_skills", "List trained skills", lambda: "trained"))
    return registry


def test_train_command_extracts_structured_arguments():
    match = ToolIntelligence(build_registry()).match(
        "train skill morning_report: Prepare my morning report | trigger: morning report | steps: open dashboard; check data | risk: medium | permissions: files"
    )
    assert match.name == "train_skill"
    assert match.arguments == {
        "name": "morning_report",
        "description": "Prepare my morning report",
        "trigger": "morning report",
        "steps": ["open dashboard", "check data"],
        "risk_level": "medium",
        "required_permissions": ["files"],
    }


def test_trainer_lifecycle_commands_extract_names():
    intelligence = ToolIntelligence(build_registry())
    assert intelligence.match("test trained skill morning_report for morning report").arguments == {
        "name": "morning_report", "query": "morning report"
    }
    assert intelligence.match("approve trained skill morning_report").arguments == {"name": "morning_report"}
    assert intelligence.match("disable trained skill morning_report").arguments == {"name": "morning_report"}
    assert intelligence.match("list my trained skills").name == "list_trained_skills"
