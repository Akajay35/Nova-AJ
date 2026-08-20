from core.permission_manager import PermissionManager
from core.permission_guard import PermissionGuard


def test_guard_blocks_without_permission(tmp_path):
    pm = PermissionManager(str(tmp_path / "permissions.json"))
    guard = PermissionGuard(pm)
    result = guard.execute("web", "network", "fetch", lambda: "ran")
    assert not result.allowed


def test_guard_runs_after_confirmation_without_persisting(tmp_path):
    pm = PermissionManager(str(tmp_path / "permissions.json"))
    pm.configure("web", "network")
    confirmations = []
    guard = PermissionGuard(
        pm,
        confirm=lambda skill, permission: confirmations.append((skill, permission)) or True,
    )

    assert guard.execute("web", "network", "fetch", lambda: "ran") == "ran"
    assert not pm.allowed("web", "network")
    assert confirmations == [("web", "network")]


def test_guard_requires_confirmation_again_for_next_execution(tmp_path):
    pm = PermissionManager(str(tmp_path / "permissions.json"))
    pm.configure("web", "network")
    calls = []

    def confirm(skill, permission):
        calls.append((skill, permission))
        return True

    guard = PermissionGuard(pm, confirm=confirm)
    assert guard.execute("web", "network", "fetch", lambda: "first") == "first"
    assert guard.execute("web", "network", "fetch", lambda: "second") == "second"
    assert calls == [("web", "network"), ("web", "network")]
