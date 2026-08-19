from __future__ import annotations

from typing import Any

from core.base_skill import BaseSkill
from core.skill_trainer import SkillTrainer


class TrainerSkill(BaseSkill):
    name = "trainer"
    description = "Create, test, activate, list, or disable user-trained skill specifications."
    keywords = ["training mode", "train skill", "teach nova", "trained skill", "skill trainer"]
    risk_level = "medium"
    required_permissions = ("skill_training",)

    def __init__(self, trainer: SkillTrainer | None = None) -> None:
        self.trainer = trainer or SkillTrainer()

    def handle(self, query: str, context: dict[str, Any] | None = None) -> str:
        """Only exposes safe status/list operations through natural-language routing.

        Actual training should be submitted through SkillTrainer.train(), which validates
        and stores a data-only specification. It never executes generated Python.
        """
        text = query.lower().strip()
        if "list" in text or "show" in text:
            skills = self.trainer.list()
            if not skills:
                return "No trained skills yet."
            return "\n".join(f"{s.name}: {s.status} ({s.risk_level})" for s in skills)
        return "Trainer mode is ready. Submit a structured skill through SkillTrainer; trained instructions are stored as data and are not executed as code."
