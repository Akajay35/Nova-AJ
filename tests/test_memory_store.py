from core.memory_store import MemoryStore

def test_memory_requires_approval(tmp_path):
    store=MemoryStore(str(tmp_path/"memory.json")); memory=store.propose("theme", "dark")
    assert not store.save(memory); assert store.search("theme") == []

def test_approved_memory_can_be_saved_and_forgotten(tmp_path):
    store=MemoryStore(str(tmp_path/"memory.json")); memory=store.propose("project", "Nova AJ", "projects")
    assert store.approve_and_save(memory); assert len(store.search("Nova")) == 1
    assert store.forget("project"); assert store.search("Nova") == []
