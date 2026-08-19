from __future__ import annotations

from typing import Any

from core.base_skill import BaseSkill
from core.skill_trainer import SkillTrainer


class TrainerSkill(BaseSkill):
    name = "trainer"
    description = "Create, test, activate, list, or disable user-trained skill specifications."
    keywords = ["training mode", "train skill", "teach nova", "trained skill", "skill trainer"]
    risk_level = "medium"
    # Training stores data-only specifications; it never executes generated code.
    # Runtime permissions are applied later when a trained skill is implemented as
    # an executable skill, so merely entering trainer mode is not privileged.
    required_permissions = ()

    def __init__(self, trainer: SkillTrainer | None = None) -> None:
        self.trainer = trainer or SkillTrainer()

    def handle(self, query: str, context: dict[str, Any] | None = None) -> str:
        text = query.lower().strip()
        if "list" in text or "show" in text:
            skills = self.trainer.list()
            if not skills:
                return "No trained skills yet."
            return "\n".join(f"{s.name}: {s.status} ({s.risk_level})" for s in skills)
        return (
            "Trainer mode is ready. Use the train_skill tool with a name, trigger, "
            "description, and steps. Training stores instructions as data and never "
            "executes generated code."
        )
