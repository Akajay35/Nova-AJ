from core.skill_security import scan_skill


def test_scanner_verification_matrix():
    cases = [
        ("import os\nos.system('echo blocked')", False),
        ("import os\nos.popen('echo blocked')", False),
        ("import importlib\nimportlib.import_module('subprocess')", False),
        ("import builtins\nbuiltins.exec('print(1)')", False),
        ("def run():\n    return 'safe'\n", True),
    ]
    for source, expected_safe in cases:
        assert scan_skill(source).safe is expected_safe


def test_scanner_blocks_dynamic_sensitive_lookup():
    report = scan_skill("import os\ngetattr(os, 'system')('echo blocked')")
    assert not report.safe
    assert any("sensitive" in finding for finding in report.findings)
