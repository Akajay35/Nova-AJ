from core.agent import Agent
from core.tool_registry import Tool, ToolRegistry
from core.tool_loop import ToolLoop

def test_tool_loop_requires_confirmation_for_risky_tool():
    registry = ToolRegistry()
    registry.register(Tool(name="demo", description="demo", handler=lambda: "done", risk_level="high"))
    loop = ToolLoop(Agent(registry))
    pending = loop.run("demo")
    assert pending.needs_confirmation is True
    assert pending.steps == 1
    done = loop.run("demo", confirm=True)
    assert done.text == "done"
