# Nova AJ Skills

A skill is a small Python module implementing `BaseSkill` and exposing `name`, `description`, `keywords`, and `handle()`.

## Add a skill

1. Copy `skills/_skill_template.py`.
2. Give the file a name ending in `_skill.py`.
3. Implement `handle()`.
4. Keep risky actions behind `PermissionGate` confirmation.
5. Restart Nova AJ; the manager discovers the module automatically.

## Skill growth

Unknown requests are recorded by `core/learning.py` as proposals. Proposals are intentionally inert. They must be reviewed, implemented, tested, and enabled by a person.

## Good skill boundaries

- One clear capability per skill.
- No API keys in source files.
- Avoid destructive operations by default.
- Validate user input.
- Return a concise spoken response.
