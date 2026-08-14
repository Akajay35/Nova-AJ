from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from core.base_skill import BaseSkill


class _SearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items: list[tuple[str, str]] = []
        self._link = ""
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            data = dict(attrs)
            href = data.get("href", "")
            if "uddg=" in href or "duckduckgo.com/l/?" in href:
                self._link = href
                self._text = []

    def handle_data(self, data):
        if self._link:
            self._text.append(data.strip())

    def handle_endtag(self, tag):
        if tag == "a" and self._link:
            title = " ".join(x for x in self._text if x)
            if title and len(self.items) < 5:
                self.items.append((title, self._link))
            self._link = ""
            self._text = []


def search_web(query: str, limit: int = 5) -> str:
    url = "https://html.duckduckgo.com/html/?q=" + quote(query)
    request = Request(url, headers={"User-Agent": "Nova-AJ/5.0"})
    with urlopen(request, timeout=8) as response:
        html = response.read().decode("utf-8", errors="ignore")
    parser = _SearchParser()
    parser.feed(html)
    if not parser.items:
        return "I couldn't find search results right now."
    lines = [f"Search results for: {query}"]
    for index, (title, link) in enumerate(parser.items[:limit], 1):
        lines.append(f"{index}. {title} — {link}")
    return "\n".join(lines)


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Searches the public web and returns a small list of result links."
    keywords = ["search the web", "web search", "search online", "look up", "google", "find online"]

    def handle(self, query: str, context: dict) -> str:
        cleaned = query
        for prefix in self.keywords:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip(" :")
                break
        if not cleaned:
            return "Tell me what you want me to search for."
        try:
            return search_web(cleaned)
        except Exception:
            return "Web search is unavailable right now."
