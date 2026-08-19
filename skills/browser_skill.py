from __future__ import annotations

import webbrowser
from urllib.parse import quote

from core.base_skill import BaseSkill


SITES = {
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
}


class BrowserSkill(BaseSkill):
    name = "browser"
    description = "Opens approved websites or performs a browser search."
    keywords = ["open youtube", "open github", "open google", "open gmail", "open chatgpt", "search browser"]
    risk_level = "medium"
    required_permissions = ("browser",)

    def matches(self, query: str) -> bool:
        q = query.lower().strip()
        return q.startswith(tuple([f"open {name}" for name in SITES] + ["search browser"]))

    def handle(self, query: str, context: dict) -> str:
        q = query.lower().strip()
        for name, url in SITES.items():
            if q == f"open {name}" or q.startswith(f"open {name} "):
                webbrowser.open(url)
                return f"Opening {name}."
        if q.startswith("search browser"):
            term = query[len("search browser"):].strip(" :")
            if not term:
                return "Tell me what to search for."
            webbrowser.open("https://www.google.com/search?q=" + quote(term))
            return f"Searching the browser for {term}."
        return "I can only open approved websites or run a browser search."
