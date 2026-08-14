from core.permission_manager import PermissionManager
from core.permission_guard import PermissionGuard

def test_guard_blocks_without_permission(tmp_path):
    pm=PermissionManager(str(tmp_path/"permissions.json")); guard=PermissionGuard(pm)
    result=guard.execute("web", "network", "fetch", lambda: "ran")
    assert not result.allowed

def test_guard_runs_after_confirmation(tmp_path):
    pm=PermissionManager(str(tmp_path/"permissions.json")); guard=PermissionGuard(pm, confirm=lambda s,p: True)
    assert guard.execute("web", "network", "fetch", lambda: "ran") == "ran"
    assert pm.allowed("web", "network")
