from core.permission_manager import PermissionManager

def test_permissions_grant_and_revoke(tmp_path):
    pm=PermissionManager(str(tmp_path/"permissions.json"))
    assert not pm.allowed("web", "network")
    pm.grant("web", "network")
    assert pm.allowed("web", "network")
    assert pm.revoke("web", "network")
    assert not pm.allowed("web", "network")
