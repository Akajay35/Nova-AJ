from core.permission_guard import PermissionGuard
from core.skill_permissions import SkillPermissions
from skills.file_skill import FileSkill


def test_file_skill_requires_files_permission(tmp_path):
    skill = FileSkill()
    skill.root = tmp_path
    permissions = SkillPermissions()
    guard = PermissionGuard(permissions)

    result = guard.execute(
        skill.name,
        "files",
        "list files",
        lambda: skill.handle("list files", {}),
    )

    assert not result.allowed


def test_file_skill_can_run_after_explicit_one_time_approval(tmp_path):
    skill = FileSkill()
    skill.root = tmp_path
    permissions = SkillPermissions()
    assert permissions.grant(skill.name, "files")
    permissions.approve_once(skill.name, "files")
    guard = PermissionGuard(permissions)

    assert guard.execute(
        skill.name,
        "files",
        "list files",
        lambda: skill.handle("list files", {}),
    ) == "Files: none"
