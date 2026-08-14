from __future__ import annotations
import webbrowser
from urllib.parse import urlparse
from core.base_skill import BaseSkill

SITES = {
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
}

class BrowserSkill(BaseSkill):
    name = "browser"
    description = "Opens an allowlisted website in the default browser."

    def matches(self, query: str) -> bool:
        q = query.lower().strip()
        return q.startswith(("open youtube", "open github", "open google", "open gmail"))

    def handle(self, query: str, context: dict) -> str:
        q = query.lower().strip()
        for name, url in SITES.items():
            if q.startswith(f"open {name}"):
                webbrowser.open(url)
                return f"Opening {name}."
        return "I can only open my approved websites right now."
