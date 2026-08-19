from __future__ import annotations

import json
import re
from typing import Any


_TOOL_STEP = re.compile(r"^tool:(?P<name>[a-zA-Z0-9_.-]+)(?:\s+(?P<args>\{.*\}))?$", re.DOTALL)


class TrainedSkillRuntime:
    """Execute only structured calls to already-registered tools.

    Free-form trained instructions are never evaluated as Python or shell code.
    Each tool call is gated by PermissionGuard before reaching ToolRegistry.
    """

    def __init__(self, trainer, tool_registry, permission_guard) -> None:
        self.trainer = trainer
        self.tools = tool_registry
        self.permissions = permission_guard

    def execute(self, skill_name: str, *, skill_label: str | None = None) -> list[Any]:
        draft = self.trainer.get(skill_name)
        if draft.status != "active":
            raise PermissionError(f"trained skill is not active: {draft.name}")

        results: list[Any] = []
        for step in draft.steps:
            match = _TOOL_STEP.fullmatch(step.strip())
            if not match:
                raise ValueError("trained step is not an allowed tool action")

            tool_name = match.group("name")
            args_text = match.group("args")
            args: dict[str, Any] = {}
            if args_text:
                parsed = json.loads(args_text)
                if not isinstance(parsed, dict):
                    raise ValueError("tool arguments must be a JSON object")
                args = parsed

            tool = self.tools.get(tool_name)
            if tool is None:
                raise KeyError(f"Unknown tool: {tool_name}")

            permission = self._permission_for(draft, tool_name)
            decision = self.permissions.check(skill_label or f"trained:{draft.name}", permission, tool_name)
            if not decision.allowed:
                raise PermissionError(decision.reason)

            results.append(self.tools.call(tool_name, **args))

        return results

    @staticmethod
    def _permission_for(draft, tool_name: str) -> str:
        """Require explicit permission mapping; never infer a powerful permission."""
        if len(draft.required_permissions) != 1:
            raise PermissionError(
                f"trained skill {draft.name} must declare exactly one runtime permission for tool {tool_name}"
            )
        return draft.required_permissions[0]
