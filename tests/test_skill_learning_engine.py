from core.skill_learning_engine import SkillLearningEngine

def test_skill_learning_requires_explicit_approval(tmp_path):
    engine=SkillLearningEngine(str(tmp_path/"proposals.json"))
    p=engine.propose("calendar", "Calendar integration", "User requested calendar support")
    assert p.status == "pending"
    assert len(engine.list_pending()) == 1
    assert engine.approve("calendar")
    assert engine.list_pending() == []
