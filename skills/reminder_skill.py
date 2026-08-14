from core.base_skill import BaseSkill
from core.reminders import ReminderStore

class ReminderSkill(BaseSkill):
    name="reminders"; description="Create and manage reminders"; keywords=["remind me","add reminder","due reminders","complete reminder"]
    def handle(self, query: str, context=None) -> str:
        store=context.get("reminders") if context else ReminderStore(); q=query.strip(); low=q.lower()
        if low.startswith("remind me ") or low.startswith("add reminder "):
            prefix="remind me " if low.startswith("remind me ") else "add reminder "
            item=store.add(q[len(prefix):].strip()); return f"Reminder {item['id']} saved."
        if "due reminders" in low: return "No reminders are due." if not store.due() else "Due: " + "; ".join(f"{x['id']}. {x['text']}" for x in store.due())
        if low.startswith("complete reminder "):
            try: rid=int(q[len("complete reminder "):].strip())
            except ValueError: return "Use: complete reminder <id>."
            return "Reminder completed." if store.complete(rid) else "Reminder not found."
        return "I can save reminders, check due reminders, or complete a reminder."
