from skills.browser_skill import BrowserSkill
from skills.file_skill import FileSkill
from skills.web_search_skill import WebSearchSkill


def test_v5_skill_matching():
    assert BrowserSkill().matches("open github")
    assert FileSkill().matches("create note hello")
    assert WebSearchSkill().matches("search the web for python")


def test_browser_does_not_match_unapproved_site():
    assert not BrowserSkill().matches("open an unknown site")
