from core.permission_manager import PermissionManager
from core.permission_guard import PermissionGuard
from core.audit_log import AuditLog
from core.action_audit import AuditedActionExecutor
from core.agent import Agent
from core.tool_registry import Tool, ToolRegistry


def test_denied_action_is_audited(tmp_path):
    pm=PermissionManager(str(tmp_path/"permissions.json")); guard=PermissionGuard(pm); log=AuditLog(str(tmp_path/"audit.json"))
    result=AuditedActionExecutor(guard, log).run("web", "network", "fetch", lambda: "ran")
    assert not result.allowed
    assert log.recent()[0]["decision"] == "denied"


def test_allowed_action_is_audited(tmp_path):
    pm=PermissionManager(str(tmp_path/"permissions.json")); pm.grant("demo", "safe")
    log=AuditLog(str(tmp_path/"audit.json")); executor=AuditedActionExecutor(PermissionGuard(pm), log)
    assert executor.run("demo", "safe", "run", lambda: "ok") == "ok"
    assert log.recent()[0]["result"] == "success"


def test_agent_confirmation_and_execution_are_audited(tmp_path):
    calls=[]; audit=AuditLog(str(tmp_path/"agent-audit.json")); registry=ToolRegistry()
    registry.register(Tool(name="send_message", description="Send a message", handler=lambda recipient, text: calls.append((recipient,text)) or "sent", risk_level="high"))
    agent=Agent(registry, audit)
    agent.execute("send_message", recipient="Sam", text="Hello")
    assert agent.confirm_pending().text == "sent"
    assert [event["decision"] for event in audit.recent()] == ["pending", "allowed", "allowed"]
    assert calls == [("Sam", "Hello")]
