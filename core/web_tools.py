from __future__ import annotations

import json
from urllib.parse import quote
from urllib.request import Request, urlopen


WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"


def web_search(query: str, limit: int = 5) -> str:
    """Search Wikipedia's public API for concise factual results.

    This intentionally uses a fixed public endpoint instead of accepting an
    arbitrary URL, keeping the assistant's network surface narrow.
    """
    text = query.strip()
    if not text:
        raise ValueError("Search query cannot be empty")
    if len(text) > 200:
        raise ValueError("Search query is too long")
    limit = max(1, min(int(limit), 5))
    url = (
        f"{WIKIPEDIA_API}?action=query&list=search&srsearch={quote(text)}"
        f"&srlimit={limit}&format=json&utf8=1"
    )
    request = Request(url, headers={"User-Agent": "Nova-AJ/273 (personal assistant)"})
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.load(response)
    except Exception as exc:
        raise RuntimeError(f"Web search failed safely: {exc}") from exc

    results = payload.get("query", {}).get("search", [])
    if not results:
        return "No web results found."
    lines = []
    for item in results:
        title = str(item.get("title", "")).strip()
        snippet = str(item.get("snippet", ""))
        snippet = snippet.replace("<span class=\"searchmatch\">", "").replace("</span>", "")
        lines.append(f"{title}: {snippet}")
    return "\n".join(lines)


def web_handlers() -> dict[str, object]:
    return {"web_search": web_search}
