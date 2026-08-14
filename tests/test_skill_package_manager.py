from core.skill_package_manager import SkillPackageManager

def test_install_and_rollback(tmp_path):
    m=SkillPackageManager(str(tmp_path/"packages.json"))
    digest=m.install("demo","1.0.0","return 1")
    assert len(digest)==64
    m.install("demo","2.0.0","return 2")
    assert m.versions("demo")[1]["active"] is True
    assert m.rollback("demo","1.0.0")
    assert m.versions("demo")[0]["active"] is True
