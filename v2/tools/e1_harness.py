"""E1 app side: drive the exclusion UI for every configuration (file://, as the archive runner).
S: tick each single row's Exclude checkbox (real change handler via click), read the re-pool, untick.
F: click "Exclude all flagged" and read the excluded set + re-pool (or refusal), then "Clear exclusions".
R: tick the pre-registered random subsets (sets.json) row by row, read the re-pool, clear.
Usage: python e1_harness.py <app_root> <sets.json> <out.json> [--ids file]"""
import json, sys, time, io
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
ARCH = Path(__file__).resolve().parents[2]
root, sets, out = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text()), Path(sys.argv[3])
corpus = json.loads((ARCH / "data" / "corpus.json").read_text(encoding="utf-8"))
ids = sorted(corpus)
if "--ids" in sys.argv: ids = [l.strip() for l in Path(sys.argv[sys.argv.index("--ids") + 1]).read_text().splitlines() if l.strip()]
Rsets = {}
for s in sets["R"]: Rsets.setdefault(s["id"], []).append(s)
JS = r"""([c, rsets]) => {
 const ta=document.querySelector('#src');
 ta.value=c.yi.map((y,i)=>`${y}, ${Math.sqrt(c.vi[i])}, row${c.rows[i]}`).join('\n');
 document.querySelector('#btn-run').click();
 const diag=window._almLastDiag(); if(!diag||diag.length!==c.yi.length) throw Error('stale or missing result');
 const boxes=[...document.querySelectorAll('#body input.excl')]; if(boxes.length!==c.yi.length) throw Error('checkbox count');
 const S=[];
 for(let i=0;i<boxes.length;i++){ boxes[i].click(); const e=window._almLastExclusion();
   if(e.excluded.length!==1||e.excluded[0]!==i) throw Error('S excluded set '+i); S.push(e.kept); boxes[i].click();
   if(window._almLastExclusion().excluded.length!==0) throw Error('S untick '+i); }
 const out={S,full:window._almLastExclusion().full};
 const fb=document.querySelector('#btn-excl-flagged');
 if(!fb.disabled){ fb.click(); const e=window._almLastExclusion(); out.F={excluded:e.excluded,kept:e.kept,refused:e.refused,
   msg:document.querySelector('#excl-msg').textContent}; document.querySelector('#btn-excl-clear').click(); }
 out.R=[];
 for(const s of rsets){ for(const i of s.exclude) boxes[i].click(); const e=window._almLastExclusion();
   out.R.push({rep:s.rep,excluded:e.excluded,kept:e.kept,refused:e.refused}); document.querySelector('#btn-excl-clear').click(); }
 if(window._almLastExclusion().excluded.length!==0) throw Error('clear failed');
 return out;
}"""
res, errs, timing = {}, [], {}
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True); pg = b.new_page(); pg.set_default_timeout(0)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((root / "influence" / "index.html").resolve().as_uri())
    pg.wait_for_function("typeof window._almLastExclusion==='function' && !!window.AlmMaCore")
    for cid in ids:
        t0 = time.time()
        try: res[cid] = pg.evaluate(JS, [corpus[cid], Rsets.get(cid, [])])
        except Exception as e: res[cid] = {"error": str(e)[:400]}
        timing[cid] = round(time.time() - t0, 2)
        print(cid, len(corpus[cid]["yi"]), timing[cid], "ERR" if "error" in res[cid] else "ok")
        out.write_text(json.dumps(res), encoding="utf-8")
    b.close()
Path(str(out) + ".meta.json").write_text(json.dumps({"pageerrors": errs, "timing": timing, "browser": "chrome"}), encoding="utf-8")
print(f"E1APP {len(res)} configurations; {len(errs)} page errors; {sum('error' in v for v in res.values())} configuration errors")
