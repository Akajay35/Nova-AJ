from core.skill_permissions import SkillPermissions

def test_permissions_require_approval():
    p = SkillPermissions()
    assert p.grant("demo", "files")
    assert not p.can_use("demo", "files")
    assert p.approve_once("demo", "files")
    assert p.can_use("demo", "files")
    p.revoke("demo", "files")
    assert not p.can_use("demo", "files")
