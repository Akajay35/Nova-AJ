from core.base_skill import BaseSkill

class ProfileSkill(BaseSkill):
    name = "profile"; description = "Manage explicit user preferences, goals and projects"; keywords = ["remember preference", "save preference", "remember goal", "remember project", "show my profile", "show my goals", "show my projects", "forget from profile"]

    def handle(self, query: str, context=None) -> str:
        assistant = context.get("assistant") if context else None
        if not assistant or not hasattr(assistant, "profile"):
            return "Profile storage is unavailable."
        q = query.strip(); low = q.lower(); p = assistant.profile
        if "show my profile" in low:
            s = p.summary(); return f"Preferences: {s['preferences'] or 'none'} | Goals: {s['goals'] or 'none'} | Projects: {s['projects'] or 'none'} | Notes: {s['notes'] or 'none'}"
        if "show my goals" in low: return "Goals: " + (" | ".join(p.summary()["goals"]) or "none")
        if "show my projects" in low: return "Projects: " + (" | ".join(p.summary()["projects"]) or "none")
        if "forget from profile" in low:
            term = q.split("forget from profile", 1)[1].strip(" :.-")
            return f"Removed {p.remove(term)} profile item(s)." if term else "Tell me what to forget."
        for marker, category in (("remember goal", "goals"), ("remember project", "projects")):
            if marker in low:
                text = q.lower().split(marker, 1)[1].strip(" :.-")
                if text: p.add(category, text); return f"Saved to your {category}."
        if "remember preference" in low or "save preference" in low:
            marker = "remember preference" if "remember preference" in low else "save preference"
            text = q.lower().split(marker, 1)[1].strip(" :.-")
            if "=" in text:
                key, value = text.split("=", 1); p.set_preference(key, value); return "Saved that preference."
            if " is " in text:
                key, value = text.split(" is ", 1); p.set_preference(key, value); return "Saved that preference."
            return "Use: remember preference <name> is <value>."
        return "I can manage your explicit preferences, goals and projects."
