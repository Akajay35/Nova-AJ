from core.personal_context import PersonalContext

def test_context_round_trip(tmp_path):
    c = PersonalContext(str(tmp_path / "context.json"))
    c.set("assistant_name", "Nova AJ")
    c.remember_event("User prefers voice control")
    assert c.get("assistant_name") == "Nova AJ"
    assert c.search("voice control")[0]["text"] == "User prefers voice control"

def test_context_is_bounded(tmp_path):
    c = PersonalContext(str(tmp_path / "context.json"), max_events=2)
    for i in range(4): c.remember_event(str(i))
    assert [x["text"] for x in c.snapshot()["events"]] == ["2", "3"]
