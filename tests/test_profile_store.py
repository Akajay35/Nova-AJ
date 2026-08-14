from core.profile_store import ProfileStore

def test_profile_set_get_remove(tmp_path):
    profile=ProfileStore(str(tmp_path/"profile.json"))
    profile.set("response_style", "concise")
    assert profile.get("response_style") == "concise"
    assert profile.summary()["response_style"] == "concise"
    assert profile.remove("response_style")
    assert profile.get("response_style") is None
