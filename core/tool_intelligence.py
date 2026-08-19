from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .tool_registry import ToolRegistry


@dataclass(frozen=True)
class ToolMatch:
    name: str | None
    arguments: dict[str, Any]
    score: int = 0


class ToolIntelligence:
    """Conservative natural-language selector for registered tools."""

    STOP_WORDS = {
        "a", "an", "and", "are", "can", "do", "for", "have", "i", "in",
        "is", "me", "my", "of", "please", "show", "the", "to", "what", "you",
    }

    SYNONYMS = {
        "system": {"system", "status", "health", "readiness", "ready", "online", "up"},
        "current_time": {"time", "clock", "timestamp", "now"},
        "calculate": {"calculate", "calculator", "compute", "math", "sum"},
        "web_search": {"search", "web", "internet", "online", "lookup", "find", "wiki", "wikipedia"},
        "set_preference": {"preference", "prefer", "preferred", "language", "voice", "style"},
        "add_goal": {"goal", "goals", "target", "objective"},
        "add_project": {"project", "projects"},
        "add_note": {"note", "notes"},
        "remove_profile_item": {"remove", "delete", "forget", "profile"},
        "search_history": {"history", "conversation", "conversations", "discussed", "talked", "said", "remember"},
        "history_for_day": {"history", "conversation", "yesterday", "today", "discussed", "talked"},
        "train_skill": {"train", "training", "teach", "skill", "learn"},
        "test_trained_skill": {"test", "testing", "trained", "skill"},
        "approve_trained_skill": {"approve", "activate", "enable", "trained", "skill"},
        "disable_trained_skill": {"disable", "deactivate", "trained", "skill"},
        "list_trained_skills": {"list", "show", "trained", "skills"},
    }

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if token not in cls.STOP_WORDS and len(token) > 1}

    @classmethod
    def _expanded_tokens(cls, text: str) -> set[str]:
        tokens = cls._tokens(text)
        expanded = set(tokens)
        for canonical, synonyms in cls.SYNONYMS.items():
            if tokens & synonyms:
                expanded.add(canonical)
        return expanded

    @staticmethod
    def _trainer_fields(text: str) -> dict[str, Any] | None:
        """Parse the intentionally simple, data-only training format."""
        pattern = re.compile(
            r"^train\s+(?:a\s+)?skill\s+(?P<name>[a-z0-9][a-z0-9_-]{1,48})\s*:\s*"
            r"(?P<description>.+?)\s*\|\s*trigger\s*:\s*(?P<trigger>.+?)\s*\|\s*"
            r"steps\s*:\s*(?P<steps>.+?)(?:\s*\|\s*risk\s*:\s*(?P<risk>low|medium|high))?"
            r"(?:\s*\|\s*permissions?\s*:\s*(?P<permissions>[^|]+))?$",
            re.IGNORECASE,
        )
        match = pattern.match(text.strip())
        if not match:
            return None
        steps = [s.strip() for s in re.split(r"\s*(?:;|\n)\s*", match.group("steps")) if s.strip()]
        permissions = [p.strip() for p in (match.group("permissions") or "").split(",") if p.strip()]
        return {
            "name": match.group("name").lower(),
            "description": match.group("description").strip(),
            "trigger": match.group("trigger").strip(),
            "steps": steps,
            "risk_level": (match.group("risk") or "low").lower(),
            "required_permissions": permissions,
        }

    def match(self, query: str) -> ToolMatch:
        text = query.strip()
        lowered = text.lower()
        if not text:
            return ToolMatch(None, {})

        # Explicit trainer commands are parsed before generic scoring so their
        # structured arguments cannot be lost to an ambiguous keyword match.
        if lowered.startswith("train skill ") or lowered.startswith("train a skill "):
            if self.tools.get("train_skill"):
                arguments = self._trainer_fields(text)
                if arguments:
                    return ToolMatch("train_skill", arguments, 100)

        for prefix in ("test trained skill ", "test skill "):
            if lowered.startswith(prefix) and self.tools.get("test_trained_skill"):
                remainder = text[len(prefix):].strip()
                parts = remainder.split(" for ", 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    return ToolMatch("test_trained_skill", {"name": parts[0].strip(), "query": parts[1].strip()}, 100)

        for prefix in ("approve trained skill ", "activate trained skill ", "enable trained skill "):
            if lowered.startswith(prefix) and self.tools.get("approve_trained_skill"):
                name = text[len(prefix):].strip()
                if name:
                    return ToolMatch("approve_trained_skill", {"name": name}, 100)

        for prefix in ("disable trained skill ", "deactivate trained skill "):
            if lowered.startswith(prefix) and self.tools.get("disable_trained_skill"):
                name = text[len(prefix):].strip()
                if name:
                    return ToolMatch("disable_trained_skill", {"name": name}, 100)

        if lowered in {"list trained skills", "show trained skills", "show my trained skills", "list my trained skills"} and self.tools.get("list_trained_skills"):
            return ToolMatch("list_trained_skills", {}, 100)

        for prefix in ("please remember that ", "remember that ", "please remember ", "remember ", "save this: "):
            if lowered.startswith(prefix) and self.tools.get("remember"):
                value = text[len(prefix):].strip()
                if value:
                    return ToolMatch("remember", {"text": value}, 100)

        history_search_patterns = (
            r"^(?:what did we|what have we) (?:discuss|talk) about (.+?)(?: recently| lately)?\??$",
            r"^(?:search|find) (?:my )?(?:conversation|chat|history) (?:for|about) (.+?)\??$",
            r"^(?:what did i|what have i) (?:say|tell you) about (.+?)\??$",
        )
        if self.tools.get("search_history"):
            for pattern in history_search_patterns:
                match = re.match(pattern, lowered)
                if match and match.group(1).strip():
                    return ToolMatch("search_history", {"term": match.group(1).strip()}, 100)

        if self.tools.get("history_for_day"):
            for prefix, day in (("what did we discuss yesterday", "yesterday"), ("what did we talk about yesterday", "yesterday"), ("show yesterday's conversation", "yesterday"), ("show yesterday conversation", "yesterday"), ("what did we discuss today", "today"), ("show today's conversation", "today")):
                if lowered.rstrip("?").strip() == prefix:
                    return ToolMatch("history_for_day", {"day": day}, 100)

        for prefix in ("can you search my memory for ", "search my memory for ", "can you search memory for ", "search memory for ", "find in memory "):
            if lowered.startswith(prefix) and self.tools.get("search_memory"):
                value = text[len(prefix):].strip()
                if value:
                    return ToolMatch("search_memory", {"term": value}, 100)

        for prefix in ("calculate ", "compute ", "what is ", "what's "):
            if lowered.startswith(prefix) and self.tools.get("calculate"):
                expression = text[len(prefix):].strip().rstrip("?")
                if expression and re.search(r"\d", expression) and re.search(r"[+\-*/%()]", expression):
                    return ToolMatch("calculate", {"expression": expression}, 100)

        if lowered in {"what time is it", "what is the time", "current time", "tell me the time"} and self.tools.get("current_time"):
            return ToolMatch("current_time", {}, 100)

        for prefix in ("search the web for ", "search web for ", "search the internet for ", "look up ", "look this up: ", "find information about ", "find info about ", "search wikipedia for ", "search wikipedia "):
            if lowered.startswith(prefix) and self.tools.get("web_search"):
                value = text[len(prefix):].strip().rstrip("?")
                if value:
                    return ToolMatch("web_search", {"query": value}, 100)

        preference_patterns = (r"^(?:please )?set (?:my )?([a-z_ ]+?) to (.+)$", r"^(?:please )?make (?:my )?([a-z_ ]+) (.+)$", r"^(?:please )?remember my preferred ([a-z_ ]+?) is (.+)$", r"^(?:please )?i prefer ([a-z_ ]+?) for ([a-z_ ]+)$")
        if self.tools.get("set_preference"):
            for pattern in preference_patterns:
                match = re.match(pattern, lowered)
                if match:
                    key, value = match.group(1).strip(), match.group(2).strip()
                    if key and value:
                        return ToolMatch("set_preference", {"key": key, "value": value}, 100)

        profile_patterns = (("add_goal", ("add a goal: ", "add goal: ", "my goal is ", "set my goal to ")), ("add_project", ("add a project: ", "add project: ", "my project is ", "set my project to ")), ("add_note", ("add a note: ", "add note: ", "save a profile note: ", "save note: ")), ("remove_profile_item", ("remove from my profile: ", "delete from my profile: ", "forget from my profile: ")))
        for tool_name, prefixes in profile_patterns:
            if self.tools.get(tool_name):
                for prefix in prefixes:
                    if lowered.startswith(prefix):
                        value = text[len(prefix):].strip()
                        if value:
                            return ToolMatch(tool_name, {"text" if tool_name != "remove_profile_item" else "term": value}, 100)

        if lowered.startswith("use "):
            parts = text[4:].split(maxsplit=1)
            if parts and self.tools.get(parts[0]):
                return ToolMatch(parts[0], {"text": parts[1]} if len(parts) == 2 else {}, 100)

        query_tokens = self._expanded_tokens(text)
        candidates: list[ToolMatch] = []
        for tool in self.tools.describe():
            name_tokens = self._expanded_tokens(tool["name"].replace("_", " "))
            desc_tokens = self._expanded_tokens(tool["description"])
            overlap = query_tokens & (name_tokens | desc_tokens)
            name_overlap = query_tokens & name_tokens
            score = len(overlap) + (2 * len(name_overlap))
            if score:
                candidates.append(ToolMatch(tool["name"], {}, score))
        if not candidates:
            return ToolMatch(None, {})
        candidates.sort(key=lambda item: (item.score, item.name or ""), reverse=True)
        best = candidates[0]
        if best.score < 2 or (len(candidates) > 1 and candidates[1].score == best.score):
            return ToolMatch(None, {})
        return best

    def plan(self, query: str) -> ToolMatch:
        return self.match(query)
