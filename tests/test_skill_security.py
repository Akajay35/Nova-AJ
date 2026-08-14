from core.skill_security import scan_skill

def test_scanner_accepts_basic_skill():
    report=scan_skill("def run():\n    return 'ok'\n")
    assert report.safe

def test_scanner_flags_dangerous_constructs():
    report=scan_skill("import subprocess\nsubprocess.run(['echo','x'])\n")
    assert not report.safe
    assert any('blocked import' in x for x in report.findings)

def test_scanner_flags_dynamic_execution():
    report=scan_skill("exec('print(1)')")
    assert not report.safe
