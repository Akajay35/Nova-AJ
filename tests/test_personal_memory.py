from core.memory import MemoryStore


def test_memory_lifecycle(tmp_path):
    path = tmp_path / "memory.json"
    memory = MemoryStore(str(path))

    first = memory.remember("I use VS Code", "preference")
    second = memory.remember("Nova AJ is my personal assistant", "fact")

    assert first["id"]
    assert memory.recent(2)[0]["text"] == "I use VS Code"
    assert memory.search("vs code")[0]["kind"] == "preference"
    assert memory.search("nova", "fact")[0]["id"] == second["id"]

    assert memory.forget(first["id"]) is True
    assert memory.search("VS Code") == []
    assert memory.forget(first["id"]) is False


def test_forget_matching_removes_multiple_memories(tmp_path):
    memory = MemoryStore(str(tmp_path / "memory.json"))
    memory.remember("I like football")
    memory.remember("Football videos are a project")
    memory.remember("I also like travel")

    assert memory.forget_matching("football") == 2
    assert len(memory.search("football")) == 0
    assert len(memory.search("travel")) == 1


def test_empty_memory_is_rejected(tmp_path):
    memory = MemoryStore(str(tmp_path / "memory.json"))
    try:
        memory.remember("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("empty memory should be rejected")
