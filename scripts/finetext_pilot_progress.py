#!/usr/bin/env python3
"""Tailscale status board for the FinetextPL-Edu pilot. Stdlib only.

Read-only: parses data/raw/finetext_pilot/sample.log, analysis.log and
pilot_reading_sample.json. Serves HTML at / and JSON at /api.
"""
import json
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "data" / "raw" / "finetext_pilot"


def read(name):
    try:
        return (PILOT / name).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def running():
    try:
        out = subprocess.run(["pgrep", "-f", "ft_analyze.py"],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        return bool(out)
    except Exception:
        return False


def summary():
    slog, alog = read("sample.log"), read("analysis.log")
    done_sample = "DONE scanned=" in slog
    done_analysis = "DONE-ANALYSIS" in alog
    sizes = {}
    for src in ("fineweb2", "finepdfs"):
        p = PILOT / f"pilot_{src}.jsonl"
        if p.exists():
            sizes[src] = {"mb": round(p.stat().st_size / 1e6),
                          "docs": sum(1 for _ in open(p, encoding="utf-8"))}
    # histogram + threshold lines straight from the log (dedupe: reruns append)
    hist, th = [], []
    for line in alog.splitlines():
        if re.match(r"\s*\[", line) and "docs=" in line:
            hist.append(line.strip())
        elif "TH>=" in line:
            th.append(line.strip())
        elif "fertility=" in line or "mean_tok=" in line or ">=" in line and "n=" in line:
            th.append(line.strip())
    hist = list(dict.fromkeys(hist))
    th = list(dict.fromkeys(th))
    prog = None
    marks = []
    for line in alog.splitlines():
        m = re.match(r"tok (\d+)/100000 elapsed=([\d.]+)s", line.strip())
        if m:
            marks.append((int(m.group(1)), float(m.group(2))))
    if marks:
        # rate from last two marks (current phase); PDFs ~6.8x longer chars
        # than web docs, so web tempo does not extrapolate: blended model.
        # order is fixed: docs 0-50000 = fineweb2, 50000-100000 = finepdfs.
        (n0, s0), (n1, s1) = marks[-2] if len(marks) > 1 else (0, 0.0), marks[-1]
        rate = (n1 - n0) / (s1 - s0) if s1 > s0 else 0
        eta = None
        if rate > 0:
            if n1 < 50000:
                eta = ((50000 - n1) / rate + 50000 / (rate / 6.8)) / 60
            else:
                eta = (100000 - n1) / rate / 60
        prog = {"pct": round(100 * n1 / 100000, 1), "n": n1,
                "rate": round(rate, 1),
                "eta_min": round(eta, 1) if eta is not None else None}
    reading = []
    try:
        reading = json.loads((PILOT / "pilot_reading_sample.json").read_text(
            encoding="utf-8"))
    except Exception:
        pass
    tail = alog.splitlines()[-6:] if alog else []
    slog_lines = [l for l in slog.splitlines()
                  if "scanned=" in l or l.startswith("DONE")]
    return {"sample_done": done_sample, "analysis_done": done_analysis,
            "analysis_running": running(), "progress": prog, "sizes": sizes,
            "sample_log": slog_lines[-4:],
            "hist": hist, "thresholds": th, "reading": reading, "tail": tail}


PAGE = """<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FinetextPL-Edu — pilot</title>
<style>
:root{--acc:#1f7a4d;--amb:#8a5a00;--mut:#5f6368;--line:#dcdcdc;--soft:#f4f6f4}
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;max-width:900px;
  margin:0 auto;padding:2em 1.2em 4em;color:#1c1c1c;line-height:1.5}
h1{font-size:1.6em;margin:0}
h2{font-size:1.05em;margin:2em 0 .4em;padding-bottom:.25em;border-bottom:2px solid var(--acc)}
.sub{color:var(--mut);margin:.2em 0 0}
.pill{display:inline-block;font-size:.78em;font-weight:600;padding:.15em .7em;
  border-radius:2em;margin-left:.6em;vertical-align:middle}
.done{background:#ddf0e3;color:#14532d}
.running{background:#fbeecb;color:#6e4c00}
.wait{background:#ececec;color:#555}
.bar{height:12px;background:#e8e8e8;border-radius:3px;overflow:hidden;margin:.5em 0}
.bar>div{height:100%;background:#1f7a4d;transition:width .5s}
table{border-collapse:collapse;width:100%;margin-top:.6em;font-size:.9em}
td,th{border:1px solid var(--line);padding:4px 8px;text-align:right;
  font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left}
thead th{background:var(--soft)}
pre{background:#f5f5f5;padding:1em;overflow:auto;font-size:12px;border:1px solid var(--line);
  white-space:pre-wrap}
.doc{border:1px solid var(--line);padding:.8em 1em;margin:.8em 0;background:#fbfbfb}
.doc .m{font-size:.82em;color:var(--mut)}
small{color:var(--mut)}
</style></head><body>
<h1>FinetextPL-Edu — pilot</h1>
<p class="sub">próbka 2×50k · histogram prediction · fertility 16k · docs ≥4 do czytania</p>
<div id="c"></div>
<script>
function pill(s){
  if(s==='done')return '<span class="pill done">gotowe</span>';
  if(s==='running')return '<span class="pill running">w toku</span>';
  return '<span class="pill wait">'+s+'</span>';
}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}
async function r(){
  const d = await (await fetch('/api')).json();
  let h = `<h2>Próbka ${pill(d.sample_done?'done':'running')}</h2>`;
  for(const [k,v] of Object.entries(d.sizes))
    h += `<p><b>${k}</b> — ${v.docs} dok., ${v.mb} MB</p>`;
  h += `<pre>${esc(d.sample_log.join('\\n'))}</pre>`;
  h += `<h2>Analiza ${pill(d.analysis_done?'done':(d.analysis_running?'running':'oczekuje'))}</h2>`;
  if(d.progress&&!d.analysis_done)
    h += `<p><b>${d.progress.pct}% zrobione</b> (${d.progress.n}/100000 dok., ` +
      `${d.progress.rate} dok/s` +
      (d.progress.eta_min!==null?`, jeszcze ok. ${d.progress.eta_min} min (PDF ~7x dluzsze)`:'') + `)</p>
      <div class="bar"><div style="width:${d.progress.pct}%"></div></div>`;
  if(d.hist.length) h += '<h2>Histogram prediction</h2><pre>'+esc(d.hist.join('\\n'))+'</pre>';
  if(d.thresholds.length) h += '<h2>Progi</h2><pre>'+esc(d.thresholds.join('\\n'))+'</pre>';
  if(d.reading.length){
    h += `<h2>20 dokumentów ≥4 do czytania</h2>`;
    for(const r of d.reading)
      h += `<div class="doc"><div class="m">${r.source} · pred ${r.prediction} · ${r.chars} znaków · ${r.tokens} tok. · ${esc(r.url||'')}</div><p>${esc(r.head400)}</p></div>`;
  }
  if(d.tail.length) h += '<h2>Koniec logu</h2><pre>'+esc(d.tail.join('\\n'))+'</pre>';
  document.getElementById('c').innerHTML = h;
}
r(); setInterval(r, 20000);
</script>
<small>Odświeżanie co 20 s · tylko odczyt plików pilota</small>
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8902
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
