#!/usr/bin/env python3
"""LAN status board for the v2.4.2 cooldown work batch. Stdlib only.

Read-only wrt the pipeline: parses train.log, eval JSONs and process state.
Serves HTML at / and JSON at /api.
"""
import datetime
import json
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CD_LOG = ROOT / "logs" / "glyph-100m-v2_4_2-15k-cooldown" / "train.log"
CD_DIR = ROOT / "checkpoints" / "glyph-100m-v2_4_2-15k-cooldown"
DOMAIN_JSON = ROOT / "reports" / "glyph100_domain_eval.json"
EOS_15K = ROOT / "eval" / "glyph-100m" / "eos_safe_15k.json"
EOS_CD = ROOT / "eval" / "glyph-100m" / "eos_safe_cooldown.json"
CD_START, CD_END = 15000, 16500

STEP_RE = re.compile(
    r"step=\s*(\d+)\s*\|\s*loss=([\d.]+)\s*\|\s*lr=([\deE.+-]+)\s*\|\s*tok/s=([\d,]+)"
)
EVAL_RE = re.compile(r"eval step=\s*(\d+)\s*\|\s*val_loss=([\d.]+)")

EVAL_TOTAL_TOK = 8280000
EVAL_TPS = 1500


def proc_elapsed(pattern: str):
    try:
        out = subprocess.run(
            ["pgrep", "-f", pattern], capture_output=True, text=True,
            timeout=5).stdout.strip().split()
    except Exception:
        return None
    for pid in out:
        try:
            ps = subprocess.run(
                ["ps", "-o", "etime=", "-p", pid], capture_output=True,
                text=True, timeout=5).stdout.strip()
        except Exception:
            continue
        if ps:
            return ps
    return None


def etime_min(s: str):
    s = s.strip()
    days = 0
    if "-" in s:
        d, s = s.split("-", 1)
        days = int(d)
    p = s.split(":")
    while len(p) < 3:
        p = ["0"] + p
    h, m, sec = (int(x) for x in p[-3:])
    return days * 1440 + h * 60 + m + sec / 60


def cooldown():
    try:
        lines = CD_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return {"state": "brak logu"}
    steps, evals = [], []
    for line in lines:
        m = STEP_RE.search(line)
        if m:
            steps.append({"step": int(m.group(1)), "loss": float(m.group(2)),
                          "lr": float(m.group(3)), "tps": int(m.group(4).replace(",", ""))})
        m = EVAL_RE.search(line)
        if m:
            evals.append({"step": int(m.group(1)), "val": float(m.group(2))})
    if not steps:
        return {"state": "brak danych"}
    last = steps[-1]
    done = last["step"] >= CD_END
    trains = [s for s in steps if s["step"] in {e["step"] for e in evals}]
    return {"state": "done" if done else "running",
            "step": last["step"], "target": CD_END,
            "pct": round(100 * (last["step"] - CD_START) / (CD_END - CD_START), 1),
            "train_loss": last["loss"], "lr": last["lr"], "tps": last["tps"],
            "evals": evals, "trains": trains,
            "first_val": evals[0]["val"] if evals else None,
            "last_val": evals[-1]["val"] if evals else None}


def ckpt_files():
    rows = []
    if CD_DIR.is_dir():
        for p in sorted(CD_DIR.glob("*.pt")):
            st = p.stat()
            rows.append({"name": p.name,
                         "mb": round(st.st_size / 1e6),
                         "mtime": datetime.datetime.fromtimestamp(
                             st.st_mtime).strftime("%H:%M:%S")})
    return rows


def domain_eval():
    if DOMAIN_JSON.exists():
        try:
            d = json.loads(DOMAIN_JSON.read_text(encoding="utf-8"))
            return {"state": "done", "full": d}
        except Exception as e:
            return {"state": "blad odczytu", "detail": str(e)[:80]}
    el = proc_elapsed("eval_domain_loss.py")
    if el:
        mins = etime_min(el)
        total = EVAL_TOTAL_TOK / EVAL_TPS / 60
        pct = min(99, round(100 * mins / total, 1))
        eta = datetime.datetime.now() + datetime.timedelta(minutes=total - mins)
        return {"state": "running", "detail": f"{mins:.0f} min z ~{total:.0f} min",
                "pct": pct, "eta_clock": eta.strftime("%H:%M")}
    return {"state": "oczekuje", "detail": "proces nie znaleziony"}


def eos_summary(path: Path):
    if not path.exists():
        el = proc_elapsed("generate_eos_safe.py")
        return {"state": "running" if el else "oczekuje"}
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        return {"state": "done", "n": d["n"], "eos": d["ended_by_eos"],
                "limit": d["hit_limit"], "mean": d["mean_len_to_eos"],
                "sec": d.get("seconds")}
    except Exception as e:
        return {"state": "blad odczytu", "detail": str(e)[:80]}


def summary():
    return {
        "now": datetime.datetime.now().strftime("%H:%M:%S"),
        "cooldown": cooldown(),
        "files": ckpt_files(),
        "domain_eval": domain_eval(),
        "eos_15k": eos_summary(EOS_15K),
        "eos_cooldown": eos_summary(EOS_CD),
        "static": {
            "A": "val_domain_parlament_clean.bin — 40 dok., 42994 tok. (usunięto 2079336, 386 tok.)",
            "C": "miks źródeł identyczny w oknach 10500–11000 i 13000–13500 (wiki ~41%) — wahania train loss to szum średniej z 10 kroków, nie kompozycja",
        },
    }


PAGE = """<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Glyph v2.4.2 — status prac</title>
<style>
:root{--acc:#1f7a4d;--amb:#8a5a00;--mut:#5f6368;--line:#dcdcdc;--bg:#fff;--soft:#f4f6f4}
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;max-width:900px;
  margin:0 auto;padding:2em 1.2em 4em;color:#1c1c1c;background:var(--bg);line-height:1.5}
header{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap}
h1{font-size:1.6em;margin:0}
h2{font-size:1.05em;margin:2em 0 .4em;padding-bottom:.25em;
  border-bottom:2px solid var(--acc)}
.sub{color:var(--mut);margin:.2em 0 0}
.pill{display:inline-block;font-size:.78em;font-weight:600;padding:.15em .7em;
  border-radius:2em;margin-left:.6em;vertical-align:middle}
.done{background:#ddf0e3;color:#14532d}
.running{background:#fbeecb;color:#6e4c00}
.wait{background:#ececec;color:#555}
.hero{display:flex;gap:2em;flex-wrap:wrap;margin:.8em 0}
.hero div{min-width:8em}
.hero .k{font-size:.78em;color:var(--mut)}
.hero .v{font-size:1.35em;font-weight:650;font-variant-numeric:tabular-nums}
.bar{height:12px;background:#e8e8e8;border-radius:3px;overflow:hidden;margin:.5em 0}
.bar>div{height:100%;background:var(--acc);transition:width .5s}
table{border-collapse:collapse;width:100%;margin-top:.6em;font-size:.92em}
td,th{border:1px solid var(--line);padding:4px 8px;text-align:right;
  font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left}
thead th{background:var(--soft)}
svg.curve{width:100%;height:150px;background:var(--soft);
  border:1px solid var(--line);margin-top:.6em}
small{color:var(--mut)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:0 2em}
@media(max-width:640px){.grid2{grid-template-columns:1fr}}
</style></head><body>
<header><div><h1>Glyph v2.4.2 — status prac</h1>
<p class="sub">cooldown 15k→16.5k · eval domenowy · generacje EOS-safe</p></div>
<div><small>aktualizacja: <span id="now"></span></small></div></header>
<div id="c"></div>
<script>
function pill(s){
  if(s==='done')return '<span class="pill done">gotowe</span>';
  if(s==='running')return '<span class="pill running">w toku</span>';
  return '<span class="pill wait">'+s+'</span>';
}
function curve(evals, trains){
  if(!evals||!evals.length)return '';
  const W=800,H=150,P=28;
  const xs=evals.map(e=>e.step), ys=evals.map(e=>e.val);
  const x0=Math.min(...xs),x1=Math.max(...xs);
  let y0=Math.min(...ys),y1=Math.max(...ys);
  const pad=(y1-y0)*0.25||0.01; y0-=pad; y1+=pad;
  const X=v=>P+(v-x0)/(x1-x0)*(W-2*P), Y=v=>H-P-(v-y0)/(y1-y0)*(H-2*P);
  const pts=evals.map(e=>X(e.step).toFixed(1)+','+Y(e.val).toFixed(1)).join(' ');
  let dots=evals.map(e=>
    `<circle cx="${X(e.step)}" cy="${Y(e.val)}" r="4" fill="#1f7a4d"/>`).join('');
  return `<svg class="curve" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <polyline points="${pts}" fill="none" stroke="#1f7a4d" stroke-width="2"/>${dots}
    <text x="${P}" y="14" font-size="12" fill="#5f6368">val ${y1.toFixed(3)}</text>
    <text x="${P}" y="${H-6}" font-size="12" fill="#5f6368">val ${y0.toFixed(3)}</text>
  </svg>`;
}
function domTable(full){
  const doms=["wikipedia","wolne_lektury","1000_novels","eltec",
    "parlament_clean","wikibooks","aggregate"];
  const cks=Object.keys(full.checkpoints||{}).filter(k=>full.checkpoints[k].cells);
  if(!cks.length)return '';
  let h='<table><thead><tr><th>domena</th>'+
    cks.map(k=>`<th>${k}</th>`).join('')+'</tr></thead>';
  for(const d of doms){
    h+='<tr><td>'+d+'</td>'+cks.map(k=>{
      const c=full.checkpoints[k].cells[d];
      return c?`<td>${c.loss.toFixed(4)}</td>`:'<td>–</td>';
    }).join('')+'</tr>';
  }
  return h+'</table>';
}
async function r(){
  const d = await (await fetch('/api')).json();
  document.getElementById('now').textContent = d.now;
  let h = '';
  const c = d.cooldown;
  h += `<h2>Trening cooldown ${pill(c.state)}</h2>`;
  if(c.step!==undefined){
    h += `<div class="hero">
      <div><div class="k">krok</div><div class="v">${c.step} / ${c.target}</div></div>
      <div><div class="k">train loss</div><div class="v">${c.train_loss}</div></div>
      <div><div class="k">val ${c.evals[c.evals.length-1].step}</div>
        <div class="v">${c.last_val} (start ${c.first_val})</div></div>
      <div><div class="k">LR</div><div class="v">${c.lr}</div></div></div>
      <div class="bar"><div style="width:${c.pct}%"></div></div>` + curve(c.evals);
    h += '<div class="grid2"><div><h2 style="border:none">Ewaluacje</h2><table><tr><th>step</th><th>val_loss</th></tr>' +
      c.evals.map(e=>`<tr><td>${e.step}</td><td>${e.val}</td></tr>`).join('') +
      '</table></div><div><h2 style="border:none">Checkpointy</h2><table><tr><th>plik</th><th>MB</th><th>zapis</th></tr>' +
      d.files.map(f=>`<tr><td>${f.name}</td><td>${f.mb}</td><td>${f.mtime}</td></tr>`).join('') +
      '</table></div></div>';
  } else h += `<p>${c.state}</p>`;
  const e = d.domain_eval;
  h += `<h2>Eval domenowy B ${pill(e.state)}</h2>`;
  if(e.state==='done'){ h += domTable(e.full); }
  else h += `<p><b>${e.pct||0}% zrobione</b>${e.eta_clock?` — koniec ok. <b>${e.eta_clock}</b>`:''}</p>
    <div class="bar"><div style="width:${e.pct||0}%"></div></div><p>${e.detail||''}</p>`;
  h += `<h2>Generacje EOS-safe (temp 0.8, top_k 40, 400 tok.)</h2>`;
  for(const [k,v] of [['15k',d.eos_15k],['cooldown',d.eos_cooldown]]){
    h += `<p><b>${k}</b> ${pill(v.state)}` +
      (v.n!==undefined?` — EOS <b>${v.eos}/${v.n}</b> (${Math.round(100*v.eos/v.n)}%), `+
        `limit ${v.limit}, śr. długość ${Math.round(v.mean)} tok., ${v.sec} s`:'') + '</p>';
  }
  h += `<h2>Wcześniej</h2><p><b>A.</b> ${d.static.A}</p><p><b>C.</b> ${d.static.C}</p>`;
  document.getElementById('c').innerHTML = h;
}
r(); setInterval(r, 15000);
</script>
<small>Odświeżanie co 15 s · tylko odczyt logów i plików wyników</small>
</body></html>
"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/api":
            body = json.dumps(summary()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        else:
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8901
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
