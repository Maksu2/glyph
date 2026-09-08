#!/usr/bin/env python3
"""Status board v2_5_1 (korekta mieszanki glyph100). Stdlib only.

Read-only: parses logs/v2_5_1/*.log, *.done, *.pid and data sizes.
Serves HTML at / and JSON at /api. Auto-refresh in page.
"""
import json
import os
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs" / "v2_5_1"
RAW = ROOT / "data" / "raw" / "glyph100_v2_5_1"

PDF_TARGET_TOK = 715_000_000  # surowe tokeny whitespace -> ~650M po filtrach
PIPE = ["ft_download", "filter1", "tokchunk", "minhash", "xref", "xref_wp",
        "build25"]
STAGE_LABEL = {
    "ft_download": "1 · Pobieranie finetext_pdf",
    "filter1": "2 · Filtr czystości",
    "tokchunk": "3 · Tokenizacja 8192",
    "minhash": "4 · MinHash wewn.",
    "xref": "5 · XRef vs v2.4.2",
    "xref_wp": "6 · XRef web×pdf",
    "build25": "7 · Build korpusu",
}
RE_SCAN = re.compile(
    r"scanned=(\d+)\s+web=\{'docs': \d+, 'tokens': \d+\}\s+"
    r"pdf=\{'docs': (\d+), 'tokens': (\d+)\}\s+elapsed=([\d.]+)s")


def read_text(path, limit=300000):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - limit))
            return f.read()
    except FileNotFoundError:
        return ""


def read_done(key):
    try:
        d = json.loads((LOGS / f"{key}.done").read_text(encoding="utf-8"))
        return {"present": True, "exit": d.get("exit"),
                "extra": {k: v for k, v in d.items() if k != "exit"}}
    except (FileNotFoundError, ValueError):
        return {"present": False, "exit": None, "extra": {}}


def pid_alive(key):
    try:
        pid = int((LOGS / f"{key}.pid").read_text().strip().split()[0])
    except (FileNotFoundError, ValueError):
        return False
    return Path(f"/proc/{pid}").exists()


def file_mb(path):
    try:
        return round(path.stat().st_size / 1e6, 1)
    except FileNotFoundError:
        return 0.0


def download_progress():
    """Parse ft_download.log -> current counts, rate, ETA."""
    marks = []
    for line in read_text(LOGS / "ft_download.log").splitlines():
        m = RE_SCAN.search(line.strip())
        if m:
            marks.append(tuple(map(float, m.groups())))
    attempts = len(re.findall(r"-- attempt \d+/", read_text(
        LOGS / "ft_download.log", 60000)))
    if not marks:
        return {"marks": 0, "attempts": attempts}
    n, docs, toks, el = marks[-1]
    rate = eta_s = None
    if len(marks) > 1:
        n0, _, t0, el0 = marks[-2]
        if el > el0 and toks >= t0:
            rate = (toks - t0) / (el - el0)
            if rate and rate > 0:
                eta_s = max(0.0, (PDF_TARGET_TOK - toks) / rate)
    return {"marks": len(marks), "scanned": int(n), "pdf_docs": int(docs),
            "pdf_tokens": int(toks), "elapsed_s": el,
            "rate_tok_s": round(rate, 1) if rate else None,
            "eta_s": round(eta_s) if eta_s else None,
            "attempts": attempts,
            "edu_pdf_mb": file_mb(RAW / "edu_pdf.jsonl"),
            "pct": round(100 * toks / PDF_TARGET_TOK, 2)}


def stage_status(key):
    done = read_done(key)
    log = read_text(LOGS / f"{key}.log", 20000)
    tail = [l for l in log.splitlines() if l.strip()][-4:]
    if done["present"]:
        st = "done" if done["exit"] == 0 else "fail"
    elif log.strip():
        st = "running"  # log rośnie, .done brak
    else:
        st = "wait"
    return {"key": key, "label": STAGE_LABEL[key], "status": st,
            "exit": done["exit"], "extra": done["extra"], "tail": tail,
            "alive": pid_alive(key)}


def summary():
    dl = download_progress()
    stages = [stage_status(k) for k in PIPE]
    overall = "running"
    if any(s["status"] == "fail" for s in stages):
        overall = "fail"
    elif stages[-1]["status"] == "done":
        overall = "done"
    return {"now": time.strftime("%H:%M:%S"), "overall": overall,
            "pdf_target_tokens": PDF_TARGET_TOK, "download": dl,
            "stages": stages,
            "mix": {"finetext_pdf": "650M (49%)",
                    "finetext_web": "450M (34%)",
                    "v2.4.2": "232M (17%)"}}


PAGE = """<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>glyph100_v2_5_1 — postęp</title>
<style>
:root{--bg:#0d100e;--panel:#141816;--line:#242b26;--txt:#e9eeea;
  --mut:#93a096;--grn:#34d17b;--amb:#e2a63d;--red:#e0655f;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--txt);margin:0;
  font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.45}
body::before{content:"";position:fixed;inset:0;pointer-events:none;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),
  linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:56px 56px;opacity:.16}
.wrap{max-width:1060px;margin:0 auto;padding:28px 20px 60px;position:relative}
.top{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
h1{font-size:22px;margin:0;font-weight:650;letter-spacing:.01em}
h1 .tag{color:var(--mut);font-weight:400}
.sub{color:var(--mut);margin:4px 0 0;font-size:13px}
.pill{display:inline-block;font-size:12.5px;font-weight:650;padding:4px 14px;
  border-radius:20px;border:1px solid var(--line);white-space:nowrap}
.pill.running{color:var(--amb);border-color:var(--amb)}
.pill.done{color:var(--grn);border-color:var(--grn)}
.pill.fail{color:var(--red);border-color:var(--red)}
.pill.wait{color:var(--mut)}
.hero{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:26px 28px;margin-top:20px}
.hero .row{display:flex;gap:28px;align-items:flex-end;flex-wrap:wrap}
.pct{font-family:var(--mono);font-size:76px;font-weight:600;line-height:1;
  color:var(--grn);font-variant-numeric:tabular-nums}
.pct small{font-size:22px;color:var(--mut)}
.tgt{font-family:var(--mono);font-size:14px;color:var(--mut);
  font-variant-numeric:tabular-nums}
.bar{height:14px;background:#0a0c0b;border:1px solid var(--line);
  border-radius:4px;margin-top:16px;position:relative;overflow:hidden}
.bar>div{height:100%;background:var(--grn);width:0}
.ticks{position:relative;height:18px;font-family:var(--mono);font-size:11px;color:var(--mut)}
.ticks span{position:absolute;transform:translateX(-50%)}
.ticks span:first-child{transform:none}
.ticks span:last-child{transform:translateX(-100%)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:8px;overflow:hidden;margin-top:18px}
.cell{background:var(--panel);padding:12px 16px}
.cell .k{font-size:12px;color:var(--mut)}
.cell .v{font-family:var(--mono);font-size:21px;margin-top:2px;
  font-variant-numeric:tabular-nums}
h2{font-size:13px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;
  color:var(--mut);margin:30px 0 10px}
.steps{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.step{background:var(--panel);border:1px solid var(--line);border-radius:6px;
  padding:10px 8px;text-align:center;font-size:12px}
.step b{display:block;font-family:var(--mono);font-size:16px;margin-bottom:2px}
.step.running{border-color:var(--amb);color:var(--amb)}
.step.done{border-color:var(--grn);color:var(--grn)}
.step.fail{border-color:var(--red);color:var(--red)}
.step.wait{color:var(--mut)}
.stage{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:14px 18px;margin-top:8px}
.stage .hd{display:flex;justify-content:space-between;gap:10px;align-items:baseline;flex-wrap:wrap}
.stage .nm{font-weight:650}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px}
.dot.running{background:var(--amb)}
.dot.done{background:var(--grn)}
.dot.fail{background:var(--red)}
.dot.wait{background:var(--mut)}
.stage .m{font-family:var(--mono);font-size:13px;color:var(--mut);margin-top:6px;
  font-variant-numeric:tabular-nums;word-break:break-word}
.mbar{height:6px;background:#0a0c0b;border-radius:3px;margin-top:8px;overflow:hidden}
.mbar>div{height:100%;background:var(--grn)}
.term{background:#070908;border:1px solid var(--line);border-radius:8px;
  padding:14px 18px;margin-top:8px;font-family:var(--mono);font-size:12.5px;
  color:#b9c6bd;white-space:pre-wrap;word-break:break-word}
.mix{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.mix .stage{text-align:left}
.mix .v{font-family:var(--mono);font-size:24px;color:var(--txt)}
footer{color:var(--mut);font-size:12px;margin-top:26px}
@media(max-width:760px){.grid,.mix{grid-template-columns:1fr}.steps{grid-template-columns:repeat(4,1fr)}.pct{font-size:56px}}
@media(prefers-reduced-motion:reduce){.bar>div{transition:none}}
</style></head><body><div class="wrap" id="c"></div>
<script>
const ST_TXT={running:['running','w toku'],done:['done','gotowe'],fail:['fail','BŁĄD'],wait:['wait','czeka']};
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function mln(n){if(n==null)return '—';n=Number(n);if(n>=1e9)return (n/1e9).toFixed(2)+' mld';if(n>=1e6)return (n/1e6).toFixed(1)+'M';if(n>=1e3)return (n/1e3).toFixed(1)+'k';return String(Math.round(n));}
function dur(s){if(s==null)return '—';s=Math.round(Number(s));const h=Math.floor(s/3600),m=Math.floor(s%3600/60);return h>0?h+' g '+m+' min':m+' min';}
async function r(){
  const d=await(await fetch('/api')).json();
  const dl=d.download, pct=dl.pct||0;
  const[oc,ot]=ST_TXT[d.overall]||ST_TXT.wait;
  let h=`<div class="top"><div><h1>glyph100_v2_5_1 <span class="tag">· korekta mieszanki</span></h1>
  <p class="sub">web:pdf 70:30 &#8594; 50:50 · literatura wraca do ~17% · aktualizacja ${esc(d.now)}</p></div>
  <span class="pill ${oc}">${ot}</span></div>`;
  h+=`<div class="hero"><div class="row"><div class="pct">${pct.toFixed(1)}<small> %</small></div>
  <div class="tgt">finetext_pdf<br>${mln(dl.pdf_tokens||0)} / ${mln(d.pdf_target_tokens)} tokenów (surowych)</div></div>
  <div class="bar"><div style="width:${pct}%"></div></div>
  <div class="ticks"><span style="left:0">0</span><span style="left:25%">25</span><span style="left:50%">50</span><span style="left:75%">75</span><span style="left:100%">100%</span></div>
  <div class="grid">
  <div class="cell"><div class="k">Dokumenty PDF</div><div class="v">${dl.pdf_docs!=null?Number(dl.pdf_docs).toLocaleString('pl-PL'):'—'}</div></div>
  <div class="cell"><div class="k">Przeskanowane wiersze</div><div class="v">${dl.scanned!=null?Number(dl.scanned).toLocaleString('pl-PL'):'—'}</div></div>
  <div class="cell"><div class="k">edu_pdf.jsonl</div><div class="v">${dl.edu_pdf_mb!=null?dl.edu_pdf_mb+' MB':'—'}</div></div>
  <div class="cell"><div class="k">Tempo</div><div class="v">${dl.rate_tok_s!=null?mln(dl.rate_tok_s)+' tok/s':'—'}</div></div>
  <div class="cell"><div class="k">ETA do celu</div><div class="v">${dur(dl.eta_s)}</div></div>
  <div class="cell"><div class="k">Retry / próby</div><div class="v">${dl.attempts||0} / 50</div></div>
  </div></div>`;
  h+=`<h2>Potok</h2><div class="steps">`;
  d.stages.forEach((s,i)=>{const[cl]=ST_TXT[s.status]||ST_TXT.wait;
    h+=`<div class="step ${cl}"><b>${i+1}</b>${esc(s.label.split('·')[1]||s.label)}</div>`;});
  h+=`</div><h2>Etapy</h2>`;
  d.stages.forEach(s=>{const[cl,tx]=ST_TXT[s.status]||ST_TXT.wait;
    h+=`<div class="stage"><div class="hd"><span class="nm"><span class="dot ${cl}"></span>${esc(s.label)}</span>
    <span class="pill ${cl}">${tx}${s.exit!==null&&s.exit!==undefined?' · exit '+s.exit:''}</span></div>`;
    const xs=Object.entries(s.extra||{}).map(([k,v])=>k+': '+v).join(' · ');
    if(xs)h+=`<div class="m">${esc(xs)}</div>`;
    if(s.tail&&s.tail.length)h+=`<div class="m">${esc(s.tail.slice(-2).join(' | '))}</div>`;
    h+=`</div>`;});
  h+=`<h2>Docelowa mieszanka ~1,33 mld</h2><div class="mix">
  <div class="stage"><div class="k sub">finetext_pdf</div><div class="v">650M · 49%</div></div>
  <div class="stage"><div class="k sub">finetext_web</div><div class="v">450M · 34%</div></div>
  <div class="stage"><div class="k sub">v2.4.2</div><div class="v">232M · 17%</div></div></div>`;
  h+=`<h2>Koniec logu pobierania</h2><div class="term">${esc((d.dl_tail||[]).join('\\n')||'(pusto)')}</div>`;
  h+=`<footer>Odświeżanie co 15 s · tylko odczyt logs/v2_5_1 i rozmiarów plików</footer>`;
  document.getElementById('c').innerHTML=h;
}
r();setInterval(r,15000);
</script></body></html>
"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/api":
            s = summary()
            s["dl_tail"] = read_text(
                LOGS / "ft_download.log").splitlines()[-6:]
            body = json.dumps(s).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        else:
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8902
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
