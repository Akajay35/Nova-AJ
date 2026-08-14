from core.base_skill import BaseSkill
from core.project_manager import ProjectManager

class ProjectSkill(BaseSkill):
    name="projects"; description="Create and track personal projects"; keywords=["create project","list projects","project progress","complete project"]
    def handle(self, query: str, context=None) -> str:
        pm=context.get("project_manager") if context else ProjectManager(); q=query.strip(); low=q.lower()
        if low.startswith("create project "):
            name=q[len("create project "):].strip(); item=pm.create(name); return f"Created project {item['id']}: {name}."
        if "list projects" in low or "project progress" in low:
            items=pm.list(); return "No projects yet." if not items else "Projects: " + "; ".join(f"{x['id']}. {x['name']} [{x['status']}]" for x in items)
        if low.startswith("complete project "):
            try: pid=int(q[len("complete project "):].strip())
            except ValueError: return "Use: complete project <id>."
            return "Project completed." if pm.update_status(pid,"completed") else "Project not found."
        return "I can create, list, or complete projects."
