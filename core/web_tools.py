from __future__ import annotations

import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen


WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_PAGE = "https://en.wikipedia.org/wiki/"


def _clean_snippet(value: object) -> str:
    text = str(value or "")
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def web_search(query: str, limit: int = 5) -> str:
    """Search Wikipedia's public API and return normalized source links.

    The network surface stays narrow: callers cannot provide an arbitrary URL.
    """
    text = query.strip()
    if not text:
        raise ValueError("Search query cannot be empty")
    if len(text) > 200:
        raise ValueError("Search query is too long")
    try:
        limit = max(1, min(int(limit), 5))
    except (TypeError, ValueError) as exc:
        raise ValueError("Result limit must be an integer") from exc

    url = (
        f"{WIKIPEDIA_API}?action=query&list=search&srsearch={quote(text)}"
        f"&srlimit={limit}&format=json&utf8=1"
    )
    request = Request(url, headers={"User-Agent": "Nova-AJ/274 (personal assistant)"})
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.load(response)
    except Exception as exc:
        raise RuntimeError(f"Web search failed safely: {exc}") from exc

    results = payload.get("query", {}).get("search", [])
    if not results:
        return "No web results found."

    lines: list[str] = []
    for item in results:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        snippet = _clean_snippet(item.get("snippet"))
        source = f"{WIKIPEDIA_PAGE}{quote(title.replace(' ', '_'))}"
        lines.append(f"{title}: {snippet}\nSource: {source}")

    return "\n\n".join(lines) if lines else "No web results found."


def web_handlers() -> dict[str, object]:
    return {"web_search": web_search}
