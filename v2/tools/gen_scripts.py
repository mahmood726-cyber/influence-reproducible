"""E3: generate the page's downloadable R script for the pre-registered sample (sets.json E3) through the page,
plus planted controls (first config of each stratum, full.mu app value + 1e-3). Usage:
python gen_scripts.py <app_root> <sets.json> <outdir>"""
import json, sys, re, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ARCH = Path(__file__).resolve().parents[2]
root, sets, outdir = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text()), Path(sys.argv[3])
outdir.mkdir(parents=True, exist_ok=True)
corpus = json.loads((ARCH / "data" / "corpus.json").read_text(encoding="utf-8"))
ids = sets["E3"]
plant = {ids[0], ids[10], ids[20]}
manifest = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True); pg = b.new_page(); pg.set_default_timeout(0)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((root / "influence" / "index.html").resolve().as_uri())
    pg.wait_for_function("typeof window.__almInfluenceRScript==='function'")
    for n, cid in enumerate(ids):
        c = corpus[cid]
        # The data are entered through the page exactly as the archive runner did (label row<n>).
        s = pg.evaluate("""c=>{const ta=document.querySelector('#src');
          ta.value=c.yi.map((y,i)=>`${y}, ${Math.sqrt(c.vi[i])}, row${c.rows[i]}`).join('\\n');
          document.querySelector('#btn-run').click(); return window.__almInfluenceRScript();}""", c)
        f = outdir / f"s{n:02d}.R"; f.write_text(s, encoding="utf-8", newline="\n")
        manifest.append({"file": f.name, "id": cid, "k": len(c["yi"]), "planted": False, "sha256": hashlib.sha256(s.encode()).hexdigest()})
        if cid in plant:
            m = re.search(r'"full\.mu" = list\(app = ([^,]+),', s)
            v = float(m.group(1)) + 1e-3
            sp = s[:m.start(1)] + repr(v) + s[m.end(1):]
            g = outdir / f"s{n:02d}_planted.R"; g.write_text(sp, encoding="utf-8", newline="\n")
            manifest.append({"file": g.name, "id": cid, "k": len(c["yi"]), "planted": True, "sha256": hashlib.sha256(sp.encode()).hexdigest()})
    b.close()
(outdir / "manifest.json").write_text(json.dumps({"scripts": manifest, "pageerrors": errs}, indent=1))
print(len(manifest), "scripts;", len(errs), "page errors")
