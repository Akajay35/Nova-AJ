from core.profile import ProfileStore

def test_profile_lifecycle(tmp_path):
    store = ProfileStore(tmp_path / "profile.json")
    store.set_preference("voice", "enabled")
    store.add("goals", "Build Nova AJ")
    store.add("projects", "Nova-AJ")
    assert store.summary()["preferences"]["voice"] == "enabled"
    assert "Build Nova AJ" in store.summary()["goals"]
    assert store.remove("Nova-AJ") == 1
    assert not store.summary()["projects"]
