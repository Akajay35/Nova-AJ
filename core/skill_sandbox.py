from __future__ import annotations
import ast
from dataclasses import dataclass

@dataclass
class SandboxResult:
    ok: bool
    message: str
    blocked: tuple[str, ...] = ()

class SkillSandbox:
    """Static safety gate for proposed skills; never executes untrusted source."""
    BLOCKED_IMPORTS = {"os", "subprocess", "socket", "ctypes", "shutil", "sys"}
    BLOCKED_CALLS = {"eval", "exec", "compile", "__import__"}

    def inspect(self, source: str) -> SandboxResult:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return SandboxResult(False, f"Syntax error: {exc}")
        blocked = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                blocked.update(a.name.split('.')[0] for a in node.names if a.name.split('.')[0] in self.BLOCKED_IMPORTS)
            elif isinstance(node, ast.ImportFrom) and node.module and node.module.split('.')[0] in self.BLOCKED_IMPORTS:
                blocked.add(node.module.split('.')[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in self.BLOCKED_CALLS:
                blocked.add(node.func.id)
        if blocked:
            return SandboxResult(False, "Blocked capability detected.", tuple(sorted(blocked)))
        return SandboxResult(True, "Static sandbox checks passed.")
