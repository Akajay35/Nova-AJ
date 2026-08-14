from core.project_manager import ProjectManager

def test_project_lifecycle(tmp_path):
    pm=ProjectManager(str(tmp_path/"projects.json")); p=pm.create("Nova AJ","Build personal assistant")
    assert p["status"] == "active"
    assert pm.update_status(p["id"],"completed")
    assert pm.list()[0]["status"] == "completed"
