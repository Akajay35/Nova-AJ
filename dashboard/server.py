from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from core.alert_config import load_cooldown, save_cooldown
from core.startup_alert_dedup import StartupAlertDeduplicator
from core.startup_alert_store import StartupAlertStore
from core.startup_alerts import build_alerts
from core.startup_health import summarize
from core.startup_issue_severity import StartupIssueSeverity

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COOLDOWN_FILE = DATA / "alert_config.json"
ALERT_STORE = StartupAlertStore(DATA / "startup_alert_history.json")
ALERT_DEDUP = StartupAlertDeduplicator(cooldown_seconds=load_cooldown(COOLDOWN_FILE))


def read_json(name, default):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def startup_events():
    return [e for e in read_json("skill_audit.json", []) if e.get("action") == "startup_diagnostics"][-10:]


def reliability(events):
    if not events:
        return {"score": None, "trend": "unknown", "checks": 0}
    recent = events[-5:]
    score = round(sum(e.get("result") == "ready" for e in recent) / len(recent) * 100)
    previous = events[-10:-5]
    previous_score = round(sum(e.get("result") == "ready" for e in previous) / len(previous) * 100) if previous else score
    trend = "improving" if score > previous_score else "declining" if score < previous_score else "stable"
    return {"score": score, "trend": trend, "checks": len(recent)}


def diagnostic_details(events, status="all", severity="all"):
    if status in {"ready", "needs_attention"}:
        events = [e for e in events if ("ready" if e.get("result") == "ready" else "needs_attention") == status]
    out = []
    for event in events:
        issues = event.get("issues", event.get("errors", [])) or []
        enriched = [{"message": str(issue), "severity": StartupIssueSeverity.label(issue)} for issue in issues]
        if severity in {"critical", "high", "medium", "low"}:
            enriched = [issue for issue in enriched if issue["severity"] == severity]
        if severity == "all" or enriched:
            out.append({"timestamp": event.get("timestamp", ""), "result": event.get("result", "unknown"), "status": "ready" if event.get("result") == "ready" else "needs_attention", "issues": enriched})
    return out


def alert_state(events):
    health = summarize(diagnostic_details(events))
    raw_alerts = build_alerts(health)
    alerts = ALERT_DEDUP.filter(raw_alerts)
    history = ALERT_STORE.sync(raw_alerts)
    return health, alerts, history


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, content_type="application/json; charset=utf-8", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        events = startup_events()
        health, alerts, history = alert_state(events)
        if path == "/":
            self._send(INDEX.encode(), "text/html; charset=utf-8"); return
        if path == "/api/status":
            self._send(json.dumps({"name":"Nova AJ","status":"online","memory":len(read_json("memory.json",[])),"tasks":len(read_json("tasks.json",[])),"profile":read_json("profile.json",{}),"skill_proposals":len(read_json("skill_proposals.json",[])),"startup_reliability":reliability(events),"startup_health":health,"startup_alerts":alerts,"startup_alert_history":history,"alert_dedup":{"cooldown_seconds":ALERT_DEDUP.cooldown_seconds}}).encode()); return
        if path == "/api/alert-config":
            self._send(json.dumps({"cooldown_seconds": ALERT_DEDUP.cooldown_seconds}).encode()); return
        if path == "/api/set-alert-cooldown":
            try:
                seconds = max(0, min(86400, int(parse_qs(parsed.query).get("seconds", ["300"])[0])))
            except ValueError:
                self._send(json.dumps({"error":"seconds must be an integer"}).encode(), status=400); return
            ALERT_DEDUP.cooldown_seconds = save_cooldown(COOLDOWN_FILE, seconds)
            self._send(json.dumps({"cooldown_seconds": ALERT_DEDUP.cooldown_seconds}).encode()); return
        if path == "/api/startup-reliability": self._send(json.dumps(reliability(events)).encode()); return
        if path == "/api/startup-health": self._send(json.dumps(health, ensure_ascii=False).encode()); return
        if path == "/api/startup-alerts": self._send(json.dumps(alerts, ensure_ascii=False).encode()); return
        if path == "/api/startup-alert-history":
            mode = parse_qs(parsed.query).get("status", ["all"])[0]
            payload = [x for x in history if mode == "all" or x.get("status") == mode]
            self._send(json.dumps(payload, ensure_ascii=False).encode()); return
        if path == "/api/startup-details":
            q=parse_qs(parsed.query); self._send(json.dumps(diagnostic_details(events,q.get("status",["all"])[0],q.get("severity",["all"])[0]),ensure_ascii=False).encode()); return
        if path == "/api/startup-history": self._send(json.dumps([{"timestamp":e.get("timestamp",""),"result":e.get("result","unknown"),"score":100 if e.get("result")=="ready" else 0} for e in events]).encode()); return
        if path == "/api/memory": self._send(json.dumps(read_json("memory.json",[]),ensure_ascii=False).encode()); return
        if path == "/api/tasks": self._send(json.dumps(read_json("tasks.json",[]),ensure_ascii=False).encode()); return
        if path == "/api/profile": self._send(json.dumps(read_json("profile.json",{}),ensure_ascii=False).encode()); return
        if path == "/api/skills": self._send(json.dumps(read_json("skill_proposals.json",[]),ensure_ascii=False).encode()); return
        self._send(b"Not found","text/plain; charset=utf-8",404)

    def log_message(self,*_args): return


INDEX=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nova AJ Control Center</title><style>body{margin:0;background:#0b1020;color:#eef2ff;font-family:system-ui}.wrap{max-width:1100px;margin:auto;padding:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}.card{background:#111a31;border:1px solid #263556;border-radius:18px;padding:20px;margin-top:16px}.value{font-size:30px;font-weight:700;margin-top:8px}.label,.muted{color:#94a3c4}.health{font-size:38px;text-transform:uppercase}.alert{border-left:4px solid #ff6b6b;padding:12px 15px;background:#261522;border-radius:10px;margin-top:10px}.alert.high{border-left-color:#ff9f43}.alert.info{border-left-color:#75e0ae}.meta{font-size:12px;color:#94a3c4;margin-top:5px}.history{max-height:320px;overflow:auto}.history-item{padding:12px 0;border-bottom:1px solid #263556}.active-state{color:#ff9f43}.resolved-state{color:#75e0ae}.filters{display:flex;gap:8px;flex-wrap:wrap}.filter{padding:9px 13px;border:1px solid #40537c;background:#172341;color:#fff;border-radius:9px;cursor:pointer}.active{outline:2px solid #7189bd}.item{padding:10px 0;border-bottom:1px solid #263556}.critical{color:#ff6b6b;font-weight:800}.high{color:#ff9f43;font-weight:700}.medium{color:#f5c16c}.low{color:#8fb3ff}.issue{font-size:13px;margin:5px 0 0 16px}.ok{color:#75e0ae}.warn{color:#f5c16c}input{padding:9px;border-radius:8px;border:1px solid #40537c;background:#172341;color:#fff;width:90px}button{color:#fff}</style></head><body><main class="wrap"><h1>Nova AJ Control Center</h1><p class="muted">Personal AI assistant system monitor</p><section class="card"><b>⚙️ Alert cooldown</b><div class="filters"><input id="cooldown" type="number" min="0" max="86400" step="1"><button class="filter" onclick="setCooldown()">Save</button><span id="cooldownMsg" class="muted"></span></div><div class="meta">0 = no cooldown · maximum 24 hours</div></section><section class="grid" id="summary"></section><section class="card"><b>🚨 Automatic startup alerts</b><div id="alerts">Loading…</div><div id="dedup" class="meta"></div></section><section class="card"><b>🕘 Persistent alert history</b><div class="filters"><button class="filter active" data-h="all">All</button><button class="filter" data-h="active">Active</button><button class="filter" data-h="resolved">Resolved</button></div><div id="alertHistory" class="history muted">Loading…</div></section><section class="card"><b>🩺 Startup diagnostics</b><div class="filters"><button class="filter active" data-s="all">All status</button><button class="filter" data-s="ready">Ready</button><button class="filter" data-s="needs_attention">Needs Attention</button></div><div class="filters"><button class="filter active" data-v="all">All severity</button><button class="filter" data-v="critical">Critical</button><button class="filter" data-v="high">High</button><button class="filter" data-v="medium">Medium</button><button class="filter" data-v="low">Low</button></div><div id="details" class="muted">Loading…</div></section></main><script>async function get(p){return(await fetch(p)).json()}function esc(x){return String(x??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\\':'&#92;'}[c]))}let status='all',severity='all',historyMode='all';async function load(){let s=await get('/api/status'),r=s.startup_reliability,h=s.startup_health,c=s.alert_dedup;document.getElementById('cooldown').value=c.cooldown_seconds;document.getElementById('summary').innerHTML=[['Health',h.health,'health'],['Critical',h.counts.critical,''],['High',h.counts.high,''],['Medium',h.counts.medium,''],['Low',h.counts.low,''],['Reliability',r.score==null?'N/A':r.score+'/100',''],['Trend',r.trend,'']].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="value ${x[2]}">${esc(x[1])}</div></div>`).join('');document.getElementById('alerts').innerHTML=s.startup_alerts.map(a=>`<div class="alert ${a.severity}"><b>${esc(a.title)}</b> — ${esc(a.count)}<div class="muted">${esc(a.action)}</div><div class="meta">Fingerprint: ${esc(a.fingerprint)} · Cooldown: ${esc(a.cooldown_seconds)}s</div></div>`).join('')||'<div class="muted">No new alerts (duplicates may be suppressed)</div>';let hist=await get('/api/startup-alert-history?status='+historyMode);document.getElementById('alertHistory').innerHTML=hist.slice().reverse().map(x=>`<div class="history-item"><b class="${x.status==='active'?'active-state':'resolved-state'}">${esc(x.status.toUpperCase())}</b> — ${esc(x.title)}<div class="muted">Severity: ${esc(x.severity)} · Issues: ${esc(x.count)}</div><div class="muted">Appeared: ${esc(x.appeared_at)}${x.resolved_at?' · Resolved: '+esc(x.resolved_at):''}</div><div class="muted">${esc(x.action)}</div></div>`).join('')||'No alert history';let d=await get('/api/startup-details?status='+status+'&severity='+severity);document.getElementById('details').innerHTML=d.slice().reverse().map(x=>`<div class="item"><b class="${x.result==='ready'?'ok':'warn'}">${x.status}</b> — ${esc(x.timestamp)}${x.issues.map(i=>`<div class="issue ${i.severity}">[${i.severity.toUpperCase()}] ${esc(i.message)}</div>`).join('')}</div>`).join('')||'No matching diagnostics'}async function setCooldown(){let n=document.getElementById('cooldown').value;let r=await get('/api/set-alert-cooldown?seconds='+encodeURIComponent(n));document.getElementById('cooldownMsg').textContent=r.error||('Saved: '+r.cooldown_seconds+' seconds');load()}document.querySelectorAll('[data-s]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-s]').forEach(x=>x.classList.remove('active'));b.classList.add('active');status=b.dataset.s;load()});document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-v]').forEach(x=>x.classList.remove('active'));b.classList.add('active');severity=b.dataset.v;load()});document.querySelectorAll('[data-h]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-h]').forEach(x=>x.classList.remove('active'));b.classList.add('active');historyMode=b.dataset.h;load()});load();setInterval(load,10000)</script></body></html>'''

def serve(host="127.0.0.1",port=8765):
    print(f"Nova AJ Control Center: http://{host}:{port}"); ThreadingHTTPServer((host,port),Handler).serve_forever()
