from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def read_json(name: str, default):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, content_type: str = "application/json; charset=utf-8", status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(INDEX.encode(), "text/html; charset=utf-8")
            return
        if path == "/api/status":
            payload = {
                "name": "Nova AJ",
                "status": "online",
                "memory": len(read_json("memory.json", [])),
                "tasks": len(read_json("tasks.json", [])),
                "profile": read_json("profile.json", {}),
                "skill_proposals": len(read_json("skill_proposals.json", [])),
            }
            self._send(json.dumps(payload).encode())
            return
        if path == "/api/memory":
            self._send(json.dumps(read_json("memory.json", []), ensure_ascii=False).encode())
            return
        if path == "/api/tasks":
            self._send(json.dumps(read_json("tasks.json", []), ensure_ascii=False).encode())
            return
        if path == "/api/profile":
            self._send(json.dumps(read_json("profile.json", {}), ensure_ascii=False).encode())
            return
        if path == "/api/skills":
            proposals = read_json("skill_proposals.json", [])
            self._send(json.dumps(proposals, ensure_ascii=False).encode())
            return
        self._send(b"Not found", "text/plain; charset=utf-8", 404)

    def log_message(self, *_args):
        return


INDEX = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nova AJ Control Center</title><style>
:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#0b1020;color:#eef2ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#18264a,#0b1020 55%);min-height:100vh}.wrap{max-width:1100px;margin:auto;padding:28px}.hero{padding:26px 0}.hero h1{font-size:42px;margin:0 0 8px}.hero p{color:#aab7d4}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}.card{background:#111a31;border:1px solid #263556;border-radius:18px;padding:20px;box-shadow:0 12px 35px #0003}.value{font-size:34px;font-weight:700;margin-top:10px}.label{color:#94a3c4}.status{display:inline-flex;gap:8px;align-items:center}.dot{width:10px;height:10px;border-radius:50%;background:#36d399}.panel{margin-top:20px}.list{max-height:260px;overflow:auto}.item{padding:10px 0;border-bottom:1px solid #263556}.muted{color:#8997b8}.refresh{margin-top:18px;padding:10px 15px;border:1px solid #40537c;background:#172341;color:#fff;border-radius:10px;cursor:pointer}
</style></head><body><main class="wrap"><section class="hero"><div class="status"><span class="dot"></span><span>Nova AJ Control Center</span></div><h1>Your personal AI assistant</h1><p>Monitor voice, memory, tasks, profile, and skill growth from one local dashboard.</p><button class="refresh" onclick="load()">Refresh</button></section><section class="grid" id="cards"></section><section class="grid panel"><div class="card"><b>👤 Profile</b><div id="profile" class="list muted">Loading…</div></div><div class="card"><b>🧠 Recent memory</b><div id="memory" class="list muted">Loading…</div></div><div class="card"><b>📋 Tasks</b><div id="tasks" class="list muted">Loading…</div></div><div class="card"><b>🧩 Skill growth</b><div id="skills" class="list muted">Loading…</div></div></section></main><script>
async function get(p){let r=await fetch(p);return r.json()}
function esc(x){return String(x??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\\':'&#92;'}[c]))}
async function load(){let s=await get('/api/status');document.getElementById('cards').innerHTML=[['Status',s.status],['Memory',s.memory],['Tasks',s.tasks],['Skill proposals',s.skill_proposals]].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="value">${esc(x[1])}</div></div>`).join('');let p=await get('/api/profile');document.getElementById('profile').innerHTML=Object.entries(p).map(([k,v])=>`<div class="item"><b>${esc(k)}</b>: ${esc(typeof v==='object'?JSON.stringify(v):v)}</div>`).join('')||'No profile data';let m=await get('/api/memory');document.getElementById('memory').innerHTML=m.slice(-10).reverse().map(x=>`<div class="item">${esc(x.text||x)}</div>`).join('')||'No memory';let t=await get('/api/tasks');document.getElementById('tasks').innerHTML=t.map(x=>`<div class="item">${esc(x.title||x.text||JSON.stringify(x))}</div>`).join('')||'No tasks';let k=await get('/api/skills');document.getElementById('skills').innerHTML=k.slice(-10).reverse().map(x=>`<div class="item"><b>${esc(x.status||'proposal')}</b> — ${esc(x.request||x.text||JSON.stringify(x))}</div>`).join('')||'No proposals'}load();setInterval(load,10000)
</script></body></html>'''


def serve(host: str = "127.0.0.1", port: int = 8765):
    print(f"Nova AJ Control Center: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
