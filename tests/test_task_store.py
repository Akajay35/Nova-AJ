from core.task_store import Task, TaskStore

def test_task_lifecycle(tmp_path):
    store=TaskStore(str(tmp_path/"tasks.json")); store.add(Task("1", "Build Nova", due_at="2026-08-15T10:00:00Z"))
    assert len(store.pending()) == 1
    assert store.complete("1")
    assert store.pending() == []

def test_task_search_and_delete(tmp_path):
    store=TaskStore(str(tmp_path/"tasks.json")); store.add(Task("1", "Learn Python"))
    assert len(store.search("python")) == 1
    assert store.delete("1")
    assert store.search("python") == []
