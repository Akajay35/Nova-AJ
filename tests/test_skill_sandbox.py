from core.skill_sandbox import SkillSandbox

def test_sandbox_blocks_dangerous_imports():
    result=SkillSandbox().inspect("import subprocess\n")
    assert not result.ok
    assert "subprocess" in result.blocked

def test_sandbox_accepts_simple_skill():
    result=SkillSandbox().inspect("def run():\n    return 'hello'\n")
    assert result.ok
