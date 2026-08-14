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
    def __init__(self): self.findings=[]
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in self.BLOCKED_IMPORTS: self.findings.append(f"blocked import: {alias.name}")
        self.generic_visit(node)
    def visit_ImportFrom(self, node):
        root=(node.module or '').split('.')[0]
        if root in self.BLOCKED_IMPORTS: self.findings.append(f"blocked import: {node.module}")
        self.generic_visit(node)
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self.SENSITIVE_CALLS: self.findings.append(f"sensitive call: {node.func.id}")
        self.generic_visit(node)

def scan_skill(source: str) -> SecurityReport:
    try: tree=ast.parse(source)
    except SyntaxError as exc: return SecurityReport(False,[f"syntax error: {exc}"])
    scanner=SkillSecurityScanner(); scanner.visit(tree)
    return SecurityReport(not scanner.findings, scanner.findings)
