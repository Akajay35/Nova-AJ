from core.skill_trainer import SkillTrainer


def test_skill_training_lifecycle(tmp_path):
    trainer = SkillTrainer(tmp_path / "trained.json")
    draft = trainer.train(
        "daily_report",
        "Prepare the daily report workflow.",
        "daily report",
        ["Validate today's data", "Prepare the report"],
        required_permissions=["files"],
    )
    assert draft.status == "draft"
    assert trainer.test("daily_report", "please run daily report")["matched"]
    active = trainer.approve("daily_report")
    assert active.status == "active"
    assert trainer.list(active_only=True)[0].name == "daily_report"
    disabled = trainer.disable("daily_report")
    assert disabled.status == "disabled"


def test_invalid_skill_name_rejected(tmp_path):
    trainer = SkillTrainer(tmp_path / "trained.json")
    try:
        trainer.train("../unsafe", "x", "x", ["x"])
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe skill name was accepted")
