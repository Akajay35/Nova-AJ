from core.permission_manager import PermissionManager
from core.permission_guard import PermissionGuard
from core.audit_log import AuditLog
from core.action_audit import AuditedActionExecutor

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
