from core.skill_security import scan_skill


def test_scanner_accepts_basic_skill():
    report = scan_skill("def run():\n    return 'ok'\n")
    assert report.safe


def test_scanner_flags_dangerous_constructs():
    report = scan_skill("import subprocess\nsubprocess.run(['echo','x'])\n")
    assert not report.safe
    assert any("blocked import" in x for x in report.findings)


def test_scanner_flags_dynamic_execution():
    report = scan_skill("exec('print(1)')")
    assert not report.safe


def test_scanner_flags_qualified_os_execution():
    report = scan_skill("import os\nos.system('echo unsafe')")
    assert not report.safe
    assert any("blocked qualified call: os.system" in x for x in report.findings)


def test_scanner_flags_dynamic_getattr_execution():
    report = scan_skill("import os\ngetattr(os, 'system')('echo unsafe')")
    assert not report.safe
    assert any("sensitive dynamic lookup: system" in x for x in report.findings)


def test_scanner_flags_dynamic_import():
    report = scan_skill("import importlib\nimportlib.import_module('subprocess')")
    assert not report.safe
    assert any("blocked qualified call: importlib.import_module" in x for x in report.findings)
