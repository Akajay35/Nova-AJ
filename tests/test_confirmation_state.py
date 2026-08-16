from core.agent import Agent
from core.tool_registry import Tool, ToolRegistry


def test_risky_tool_requires_confirmation_then_executes():
    calls = []
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="send_message",
            description="Send a message to another person",
            handler=lambda recipient, text: calls.append((recipient, text)) or "sent",
            risk_level="high",
        )
    )
    agent = Agent(registry)

    blocked = agent.execute("send_message", recipient="Sam", text="Hello")
    assert blocked.requires_confirmation is True
    assert calls == []

    result = agent.confirm_pending()
    assert result.text == "sent"
    assert calls == [("Sam", "Hello")]
    assert agent.confirm_pending().text == "There is no pending action to confirm."


def test_pending_action_can_be_cancelled():
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="send_message",
            description="Send a message to another person",
            handler=lambda recipient, text: "sent",
            risk_level="high",
        )
    )
    agent = Agent(registry)
    agent.execute("send_message", recipient="Sam", text="Hello")
    result = agent.cancel_pending()
    assert result.text == "Cancelled the pending send_message action."
