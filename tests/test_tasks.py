from core.task_manager import TaskManager


def test_task_lifecycle(tmp_path):
    manager = TaskManager(str(tmp_path / "tasks.json"))
    task = manager.add("Build Nova AJ")
    assert task.id == 1
    assert len(manager.list_open()) == 1
    assert manager.complete(1) is True
    assert manager.list_open() == []
