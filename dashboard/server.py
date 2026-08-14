from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def read_json(name: str, default):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def startup_events():
    audit = read_json("skill_audit.json", [])
    return [e for e in audit if e.get("action") == "startup_diagnostics"][-10:]


def reliability(events):
    if not events:
        return {"score": None, "trend": "unknown", "checks": 0}
    recent = events[-5:]
    ready = sum(e.get("result") == "ready" for e in recent)
    score = round(ready / len(recent) * 100)
    if len(events) > len(recent):
        previous = events[-10:-5]
        previous_score = round(sum(e.get("result") == "ready" for e in previous) / len(previous) * 100) if previous else score
        trend = "improving" if score > previous_score else "declining" if score < previous_score else "stable"
    else:
        trend = "stable"
    return {"score": score, "trend": trend, "checks": len(recent)}


def history_payload(events):
    return [{"timestamp": e.get("timestamp", ""), "result": e.get("result", "unknown"), "score": 100 if e.get("result") == "ready" else 0} for e in events]


def diagnostic_details(events, status="all"):
    if status in {"ready", "needs_attention"}:
        events = [e for e in events if ("ready" if e.get("result") == "ready" else "needs_attention") == status]
    return [
        {
            "timestamp": e.get("timestamp", ""),
            "result": e.get("result", "unknown"),
            "status": "ready" if e.get("result") == "ready" else "needs_attention",
            "issues": e.get("issues", e.get("errors", [])) or [],
        }
        for e in events
    ]


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, content_type: str = "application/json; charset=utf-8", status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        events = startup_events()
        if path == "/":
            self._send(INDEX.encode(), "text/html; charset=utf-8")
            return
        if path == "/api/status":
            payload = {"name":"Nova AJ","status":"online","memory":len(read_json("memory.json",[])),"tasks":len(read_json("tasks.json",[])),"profile":read_json("profile.json",{}),"skill_proposals":len(read_json("skill_proposals.json",[])),"startup_reliability":reliability(events)}
            self._send(json.dumps(payload).encode()); return
        if path == "/api/memory": self._send(json.dumps(read_json("memory.json",[]),ensure_ascii=False).encode()); return
        if path == "/api/tasks": self._send(json.dumps(read_json("tasks.json",[]),ensure_ascii=False).encode()); return
        if path == "/api/profile": self._send(json.dumps(read_json("profile.json",{}),ensure_ascii=False).encode()); return
        if path == "/api/skills": self._send(json.dumps(read_json("skill_proposals.json",[]),ensure_ascii=False).encode()); return
        if path == "/api/startup-reliability": self._send(json.dumps(reliability(events)).encode()); return
        if path == "/api/startup-history": self._send(json.dumps(history_payload(events),ensure_ascii=False).encode()); return
        if path == "/api/startup-details":
            status = parse_qs(parsed.query).get("status", ["all"])[0]
            if status not in {"all", "ready", "needs_attention"}:
                status = "all"
            self._send(json.dumps(diagnostic_details(events, status),ensure_ascii=False).encode()); return
        self._send(b"Not found", "text/plain; charset=utf-8", 404)

    def log_message(self, *_args):
        return


INDEX = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nova AJ Control Center</title><style>
:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#0b1020;color:#eef2ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#18264a,#0b1020 55%);min-height:100vh}.wrap{max-width:1100px;margin:auto;padding:28px}.hero{padding:26px 0}.hero h1{font-size:42px;margin:0 0 8px}.hero p{color:#aab7d4}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}.card{background:#111a31;border:1px solid #263556;border-radius:18px;padding:20px;box-shadow:0 12px 35px #0003}.value{font-size:34px;font-weight:700;margin-top:10px}.label{color:#94a3c4}.status{display:inline-flex;gap:8px;align-items:center}.dot{width:10px;height:10px;border-radius:50%;background:#36d399}.panel{margin-top:20px}.list{max-height:260px;overflow:auto}.item{padding:10px 0;border-bottom:1px solid #263556}.muted{color:#8997b8}.refresh,.filter{margin-top:18px;padding:10px 15px;border:1px solid #40537c;background:#172341;color:#fff;border-radius:10px;cursor:pointer}.filter.active{outline:2px solid #7189bd}.filters{display:flex;gap:8px;flex-wrap:wrap}.chart{display:flex;align-items:end;gap:10px;height:150px;margin-top:15px}.bar{flex:1;min-width:18px;background:#52688f;border-radius:8px 8px 2px 2px;position:relative}.bar span{position:absolute;bottom:100%;left:50%;transform:translateX(-50%);font-size:11px;color:#aab7d4;margin-bottom:4px}.axis{display:flex;gap:10px;color:#7181a2;font-size:10px}.axis div{flex:1;text-align:center;overflow:hidden;text-overflow:ellipsis}.ok{color:#75e0ae}.warn{color:#f5c16c}.issue{margin:6px 0 0 18px;color:#f3b8b8;font-size:13px}
</style></head><body><main class="wrap"><section class="hero"><div class="status"><span class="dot"></span><span>Nova AJ Control Center</span></div><h1>Your personal AI assistant</h1><p>Monitor voice, memory, tasks, profile, skill growth, and startup reliability from one local dashboard.</p><button class="refresh" onclick="load()">Refresh</button></section><section class="grid" id="cards"></section><section class="card panel"><b>📈 Startup reliability history</b><div id="history" class="chart"></div><div id="axis" class="axis"></div></section><section class="card panel"><b>🩺 Startup diagnostic details</b><div class="filters"><button class="filter active" data-filter="all">All</button><button class="filter" data-filter="ready">Ready</button><button class="filter" data-filter="needs_attention">Needs Attention</button></div><div id="details" class="list muted">Loading…</div></section><section class="grid panel"><div class="card"><b>👤 Profile</b><div id="profile" class="list muted">Loading…</div></div><div class="card"><b>🧠 Recent memory</b><div id="memory" class="list muted">Loading…</div></div><div class="card"><b>📋 Tasks</b><div id="tasks" class="list muted">Loading…</div></div><div class="card"><b>🧩 Skill growth</b><div id="skills" class="list muted">Loading…</div></div></section></main><script>
async function get(p){let r=await fetch(p);return r.json()}function esc(x){return String(x??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\\':'&#92;'}[c]))}
async function loadDetails(filter='all'){let d=await get('/api/startup-details?status='+encodeURIComponent(filter));document.getElementById('details').innerHTML=d.slice().reverse().map(x=>`<div class="item"><b class="${x.result==='ready'?'ok':'warn'}">${esc(x.status)}</b> — ${esc(x.timestamp)}${x.issues?.length?`<div>${x.issues.map(i=>`<div class="issue">• ${esc(typeof i==='string'?i:JSON.stringify(i))}</div>`).join('')}</div>`:''}</div>`).join('')||'No matching startup diagnostics'}
async function load(){let s=await get('/api/status'),r=s.startup_reliability||{};document.getElementById('cards').innerHTML=[['Status',s.status],['Memory',s.memory],['Tasks',s.tasks],['Skill proposals',s.skill_proposals],['Startup reliability',r.score==null?'N/A':r.score+'/100'],['Reliability trend',r.trend||'unknown']].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="value">${esc(x[1])}</div></div>`).join('');let h=await get('/api/startup-history');document.getElementById('history').innerHTML=h.length?h.map(x=>`<div class="bar" style="height:${Math.max(12,x.score)}%"><span>${x.score}%</span></div>`).join(''):'<div class="muted">No startup history yet.</div>';document.getElementById('axis').innerHTML=h.map(x=>`<div>${esc(x.timestamp)}</div>`).join('');await loadDetails(document.querySelector('.filter.active')?.dataset.filter||'all');let p=await get('/api/profile');document.getElementById('profile').innerHTML=Object.entries(p).map(([k,v])=>`<div class="item"><b>${esc(k)}</b>: ${esc(typeof v==='object'?JSON.stringify(v):v)}</div>`).join('')||'No profile data';let m=await get('/api/memory');document.getElementById('memory').innerHTML=m.slice(-10).reverse().map(x=>`<div class="item">${esc(x.text||x)}</div>`).join('')||'No memory';let t=await get('/api/tasks');document.getElementById('tasks').innerHTML=t.map(x=>`<div class="item">${esc(x.title||x.text||JSON.stringify(x))}</div>`).join('')||'No tasks';let k=await get('/api/skills');document.getElementById('skills').innerHTML=k.slice(-10).reverse().map(x=>`<div class="item"><b>${esc(x.status||'proposal')}</b> — ${esc(x.request||x.text||JSON.stringify(x))}</div>`).join('')||'No proposals'}document.querySelectorAll('.filter').forEach(b=>b.onclick=()=>{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');loadDetails(b.dataset.filter)});load();setInterval(load,10000)
</script></body></html>'''


def serve(host: str = "127.0.0.1", port: int = 8765):
    print(f"Nova AJ Control Center: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
