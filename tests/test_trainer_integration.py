from core.assistant import NovaAssistant


def test_trainer_tools_are_registered(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assistant = NovaAssistant()
    names = assistant.tools.names()
    assert "train_skill" in names
    assert "test_trained_skill" in names
    assert "approve_trained_skill" in names
    assert "disable_trained_skill" in names
    assert "list_trained_skills" in names
