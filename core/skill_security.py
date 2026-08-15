from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass
class SecurityReport:
    safe: bool
    findings: list[str]


class SkillSecurityScanner(ast.NodeVisitor):
    BLOCKED_IMPORTS = {"subprocess", "ctypes", "socket", "shutil"}
    SENSITIVE_CALLS = {"eval", "exec", "compile", "__import__"}
    BLOCKED_QUALIFIED_CALLS = {
        "os.system",
        "os.popen",
        "os.spawnl",
        "os.spawnle",
        "os.spawnlp",
        "os.spawnlpe",
        "os.spawnv",
        "os.spawnve",
        "os.spawnvp",
        "os.spawnvpe",
        "os.execl",
        "os.execle",
        "os.execlp",
        "os.execlpe",
        "os.execv",
        "os.execve",
        "os.execvp",
        "os.execvpe",
        "posix.system",
        "posix.popen",
        "importlib.import_module",
        "builtins.eval",
        "builtins.exec",
        "builtins.compile",
        "builtins.__import__",
    }
    SENSITIVE_GETATTR_NAMES = SENSITIVE_CALLS | {
        "system",
        "popen",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
        "execl",
        "execle",
        "execlp",
        "execlpe",
        "execv",
        "execve",
        "execvp",
        "execvpe",
        "import_module",
    }

    def __init__(self):
        self.findings: list[str] = []

    @staticmethod
    def _qualified_name(node: ast.AST) -> str | None:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            return ".".join(reversed(parts))
        return None

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.split(".")[0] in self.BLOCKED_IMPORTS:
                self.findings.append(f"blocked import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").split(".")[0]
        if root in self.BLOCKED_IMPORTS:
            self.findings.append(f"blocked import: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in self.SENSITIVE_CALLS:
            self.findings.append(f"sensitive call: {node.func.id}")

        qualified = self._qualified_name(node.func)
        if qualified in self.BLOCKED_QUALIFIED_CALLS:
            self.findings.append(f"blocked qualified call: {qualified}")

        # Catch common dynamic capability lookup such as getattr(os, "system").
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
            and node.args[1].value in self.SENSITIVE_GETATTR_NAMES
        ):
            self.findings.append(f"sensitive dynamic lookup: {node.args[1].value}")

        self.generic_visit(node)


def scan_skill(source: str) -> SecurityReport:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return SecurityReport(False, [f"syntax error: {exc}"])
    scanner = SkillSecurityScanner()
    scanner.visit(tree)
    return SecurityReport(not scanner.findings, scanner.findings)
