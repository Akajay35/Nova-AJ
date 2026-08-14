from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from core.startup_issue_severity import StartupIssueSeverity

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def read_json(name, default):
    try: return json.loads((DATA / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return default

def startup_events():
    return [e for e in read_json("skill_audit.json", []) if e.get("action") == "startup_diagnostics"][-10:]

def reliability(events):
    if not events: return {"score": None, "trend": "unknown", "checks": 0}
    recent=events[-5:]; score=round(sum(e.get("result")=="ready" for e in recent)/len(recent)*100)
    previous=events[-10:-5]
    previous_score=round(sum(e.get("result")=="ready" for e in previous)/len(previous)*100) if previous else score
    return {"score":score,"trend":"improving" if score>previous_score else "declining" if score<previous_score else "stable","checks":len(recent)}

def diagnostic_details(events, status="all", severity="all"):
    if status in {"ready","needs_attention"}: events=[e for e in events if ("ready" if e.get("result")=="ready" else "needs_attention")==status]
    out=[]
    for e in events:
        issues=e.get("issues",e.get("errors",[])) or []
        enriched=[{"message":str(i),"severity":StartupIssueSeverity.label(i)} for i in issues]
        if severity in {"critical","high","medium","low"}: enriched=[i for i in enriched if i["severity"]==severity]
        if severity not in {"all","critical","high","medium","low"} or severity=="all" or enriched:
            out.append({"timestamp":e.get("timestamp",""),"result":e.get("result","unknown"),"status":"ready" if e.get("result")=="ready" else "needs_attention","issues":enriched})
    return out

class Handler(BaseHTTPRequestHandler):
    def _send(self, body, content_type="application/json; charset=utf-8", status=200):
        self.send_response(status); self.send_header("Content-Type",content_type); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p=urlparse(self.path); path=p.path; events=startup_events()
        if path=="/": self._send(INDEX.encode(),"text/html; charset=utf-8"); return
        if path=="/api/status": self._send(json.dumps({"name":"Nova AJ","status":"online","memory":len(read_json("memory.json",[])),"tasks":len(read_json("tasks.json",[])),"profile":read_json("profile.json",{}),"skill_proposals":len(read_json("skill_proposals.json",[])),"startup_reliability":reliability(events)}).encode()); return
        if path=="/api/startup-reliability": self._send(json.dumps(reliability(events)).encode()); return
        if path=="/api/startup-details":
            q=parse_qs(p.query); status=q.get("status",["all"])[0]; severity=q.get("severity",["all"])[0]
            self._send(json.dumps(diagnostic_details(events,status,severity),ensure_ascii=False).encode()); return
        if path=="/api/startup-history": self._send(json.dumps([{"timestamp":e.get("timestamp",""),"result":e.get("result","unknown"),"score":100 if e.get("result")=="ready" else 0} for e in events]).encode()); return
        if path=="/api/memory": self._send(json.dumps(read_json("memory.json",[]),ensure_ascii=False).encode()); return
        if path=="/api/tasks": self._send(json.dumps(read_json("tasks.json",[]),ensure_ascii=False).encode()); return
        if path=="/api/profile": self._send(json.dumps(read_json("profile.json",{}),ensure_ascii=False).encode()); return
        if path=="/api/skills": self._send(json.dumps(read_json("skill_proposals.json",[]),ensure_ascii=False).encode()); return
        self._send(b"Not found","text/plain; charset=utf-8",404)
    def log_message(self,*_args): return

INDEX=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nova AJ Control Center</title><style>body{margin:0;background:#0b1020;color:#eef2ff;font-family:system-ui}.wrap{max-width:1100px;margin:auto;padding:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px}.card{background:#111a31;border:1px solid #263556;border-radius:18px;padding:20px;margin-top:16px}.value{font-size:30px;font-weight:700;margin-top:8px}.label,.muted{color:#94a3c4}.filters{display:flex;gap:8px;flex-wrap:wrap}.filter{padding:9px 13px;border:1px solid #40537c;background:#172341;color:#fff;border-radius:9px;cursor:pointer}.active{outline:2px solid #7189bd}.item{padding:10px 0;border-bottom:1px solid #263556}.critical{color:#ff6b6b;font-weight:800}.high{color:#ff9f43;font-weight:700}.medium{color:#f5c16c}.low{color:#8fb3ff}.issue{font-size:13px;margin:5px 0 0 16px}.ok{color:#75e0ae}.warn{color:#f5c16c}</style></head><body><main class="wrap"><h1>Nova AJ Control Center</h1><p class="muted">Personal AI assistant system monitor</p><section class="grid" id="cards"></section><section class="card"><b>🩺 Startup diagnostics</b><div class="filters"><button class="filter active" data-s="all">All status</button><button class="filter" data-s="ready">Ready</button><button class="filter" data-s="needs_attention">Needs Attention</button></div><div class="filters"><button class="filter active" data-v="all">All severity</button><button class="filter" data-v="critical">Critical</button><button class="filter" data-v="high">High</button><button class="filter" data-v="medium">Medium</button><button class="filter" data-v="low">Low</button></div><div id="details" class="muted">Loading…</div></section></main><script>async function get(p){return(await fetch(p)).json()}function esc(x){return String(x??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\\':'&#92;'}[c]))}let status='all',severity='all';async function load(){let s=await get('/api/status'),r=s.startup_reliability;document.getElementById('cards').innerHTML=[['Status',s.status],['Memory',s.memory],['Tasks',s.tasks],['Reliability',r.score==null?'N/A':r.score+'/100'],['Trend',r.trend]].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="value">${esc(x[1])}</div></div>`).join('');let d=await get('/api/startup-details?status='+status+'&severity='+severity);document.getElementById('details').innerHTML=d.slice().reverse().map(x=>`<div class="item"><b class="${x.result==='ready'?'ok':'warn'}">${x.status}</b> — ${esc(x.timestamp)}${x.issues.map(i=>`<div class="issue ${i.severity}">[${i.severity.toUpperCase()}] ${esc(i.message)}</div>`).join('')}</div>`).join('')||'No matching diagnostics'}document.querySelectorAll('[data-s]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-s]').forEach(x=>x.classList.remove('active'));b.classList.add('active');status=b.dataset.s;load()});document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-v]').forEach(x=>x.classList.remove('active'));b.classList.add('active');severity=b.dataset.v;load()});load();setInterval(load,10000)</script></body></html>'''

def serve(host="127.0.0.1",port=8765):
    print(f"Nova AJ Control Center: http://{host}:{port}"); ThreadingHTTPServer((host,port),Handler).serve_forever()
