"""E2 comparator: credit the archived-but-uncredited metafor 5.2-1 reference fields against the page's new
LOO / DFBETAS / full-model outputs, read from a harness.py capture of the page (diag + full objects).
Usage: python e2_compare.py capture.json label [--plant]"""
import json, sys, copy
from pathlib import Path
ARCH = Path(__file__).resolve().parents[2]
app = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); label = sys.argv[2]
ref = json.loads((ARCH / "results" / "reference.json").read_text(encoding="utf-8"))
corpus = json.loads((ARCH / "data" / "corpus.json").read_text(encoding="utf-8"))
if "--plant" in sys.argv:
    app = copy.deepcopy(app); f = sorted(app)[0]
    app[f]["diag"][0]["loo_tau2"] *= 1 + 1e-4
    app[f]["full"]["Qp"] = (app[f]["full"]["Qp"] or 0) + 1e-8
    app[f]["diag"][1]["dfbetas"] += 2e-6
stats, fails = {}, []


def chk(q, x, y, cid, row=None, tol=1e-6):
    s = stats.setdefault(q, dict(checks=0, passes=0, max=0.0, tol=tol, worst=None))
    s["checks"] += 1
    if x is None or y is None:
        err = 0.0 if x is None and y is None else float("inf")
    else:
        err = abs(x - y) / max(1.0, abs(y))
    if err <= tol:
        s["passes"] += 1
    else:
        fails.append(dict(q=q, id=cid, row=row, app=x, ref=y, err=err))
    if err > s["max"]:
        s["max"], s["worst"] = err, [cid, row]


ROW = [("loo.tau2", "loo_tau2", ("loo", "tau2"), 1e-6), ("loo.I2", "loo_I2", ("loo", "I2"), 1e-6), ("loo.H2", "loo_H2", ("loo", "H2"), 1e-6),
       ("loo.Q", "loo_Q", ("loo", "Q"), 1e-9), ("loo.Qp", "loo_Qp", ("loo", "Qp"), 1e-9), ("loo.zval", "loo_z", ("loo", "zval"), 1e-6),
       ("loo.pval", "loo_p", ("loo", "pval"), 1e-6), ("inf.tau2.del", "loo_tau2", ("inf", "tau2.del"), 1e-6),
       ("inf.QE.del", "loo_Q", ("inf", "QE.del"), 1e-9), ("dfbetas.intrcpt", "dfbetas", ("dfbetas", "intrcpt"), 1e-6)]
FULL = [("full.ciLo", "ciLo", 1e-6), ("full.ciHi", "ciHi", 1e-6), ("full.p", "p", 1e-6), ("full.I2", "I2", 1e-6), ("full.Qp", "Qp", 1e-9)]
missing = []
for cid in sorted(corpus):
    a = app.get(cid)
    if not a or "error" in a or len(a["diag"]) != len(corpus[cid]["yi"]):
        missing.append(cid); continue
    r = ref[cid]
    for q, aq, tol in FULL:
        chk(q, a["full"].get(aq, "MISSING") if aq in a["full"] else float("nan"), r["full"][aq], cid, None, tol)
    for i, d in enumerate(a["diag"]):
        for q, aq, (g, f), tol in ROW:
            chk(q, d[aq] if aq in d else float("nan"), r[g][f][i], cid, i, tol)
out = [f"[{label}] configurations: {len(corpus) - len(missing)}/{len(corpus)}; missing {missing}",
       "quantity | pass/checks | max normalized diff | tol | worst"]
for q, s in stats.items():
    out.append(f"{q} | {s['passes']}/{s['checks']} | {s['max']:.3e} | {s['tol']} | {s['worst']}")
ps = sum(s["passes"] for s in stats.values()); n = sum(s["checks"] for s in stats.values())
out.append(f"E2 TOTAL {ps}/{n} checks pass")
txt = "\n".join(out); print(txt)
Path(f"e2_compare_{label}.txt").write_text(txt + "\n", encoding="utf-8")
Path(f"e2_failures_{label}.json").write_text(json.dumps(fails[:500], indent=1), encoding="utf-8")
sys.exit(0 if not fails and not missing else 1)
