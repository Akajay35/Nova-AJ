from core.base_skill import BaseSkill


class MemorySearchSkill(BaseSkill):
    name = "memory_search"
    description = "Search saved local memory."
    keywords = ["what do you remember", "search memory", "remember about", "what did i tell you"]

    def handle(self, query: str, context=None) -> str:
        memory = context.get("memory") if context else None
        if not memory:
            return "Local memory is unavailable."
        q = query.lower()
        for prefix in self.keywords:
            if q.startswith(prefix):
                term = query[len(prefix):].strip(" :,-")
                break
        else:
            term = query
        if not term:
            items = memory.recent(5)
        else:
            items = memory.search(term)[:5]
        if not items:
            return "I couldn't find anything matching that in local memory."
        return "I remember: " + "; ".join(x.get("text", "") for x in items)
