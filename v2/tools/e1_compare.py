"""E1 comparator. App exclusion re-pools (e1_harness output) vs metafor 5.2-1:
S vs archived leave1out (reference.json), F/R vs new pre-registered refits (refits.jsonl).
Normalized difference |app-R|/max(1,|R|) (archive rule); REML 1e-6, QE/QEp 1e-9, k and sets exact.
Usage: python e1_compare.py app.json refits.jsonl sets.json label [--plant]"""
import json, sys, copy
from pathlib import Path
ARCH = Path(__file__).resolve().parents[2]
app = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
ref = json.loads((ARCH / "results" / "reference.json").read_text(encoding="utf-8"))
corpus = json.loads((ARCH / "data" / "corpus.json").read_text(encoding="utf-8"))
lines = [json.loads(l) for l in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines() if l.strip()]
sets = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")); label = sys.argv[4]
env = lines[0]["env"]; assert lines[-1].get("done") is True, "refit run incomplete"
refits = {}
for r in lines[1:-1]:
    assert "error" not in r, r
    refits[(r["tag"], r["id"])] = r
if "--plant" in sys.argv:
    app = copy.deepcopy(app); a0 = app[sorted(app)[0]]
    a0["S"][0]["tau2"] *= 1 + 1e-4                            # planted REML defect
    fid = sorted(i for i in app if "F" in app[i] and app[i]["F"]["kept"])[0]
    app[fid]["F"]["kept"]["k"] += 1                            # planted k defect
    app[fid]["F"]["excluded"] = app[fid]["F"]["excluded"][1:]  # planted set defect
    rid = sorted(i for i in app if app[i].get("R"))[0]
    app[rid]["R"][0]["kept"]["Q"] *= 1 + 1e-8                  # planted Q defect
stats, fails = {}, []


def chk(set_, q, x, y, cid, row=None, tol=1e-6):
    s = stats.setdefault((set_, q), dict(checks=0, passes=0, max=0.0, tol=tol))
    s["checks"] += 1
    if x is None or y is None:
        err = 0.0 if x is None and y is None else float("inf")
    elif isinstance(x, (list, bool)) or tol == 0:
        err = 0.0 if x == y else float("inf")
    else:
        err = abs(x - y) / max(1.0, abs(y))
    if err <= tol:
        s["passes"] += 1
    else:
        fails.append(dict(set=set_, q=q, id=cid, row=row, app=x, ref=y, err=err))
    s["max"] = max(s["max"], err)


MAP = [("mu", "estimate", "mu", 1e-6), ("seMu", "se", "se", 1e-6), ("ciLo", "ci.lb", "ci.lb", 1e-6), ("ciHi", "ci.ub", "ci.ub", 1e-6),
       ("z", "zval", "zval", 1e-6), ("p", "pval", "pval", 1e-6), ("tau2", "tau2", "tau2", 1e-6), ("I2", "I2", "I2", 1e-6),
       ("H2", "H2", "H2", 1e-6), ("Q", "Q", "QE", 1e-9), ("Qp", "Qp", "QEp", 1e-9)]
missing = [i for i in corpus if i not in app or "error" in app[i]]
for cid in sorted(corpus):
    a = app.get(cid)
    if a is None or "error" in a:
        continue
    k = len(corpus[cid]["yi"]); L = ref[cid]["loo"]
    chk("S", "rows", len(a["S"]), k, cid, tol=0)
    for i, kept in enumerate(a["S"]):
        for aq, lq, _, tol in MAP:
            chk("S", aq, kept[aq], L[lq][i], cid, i, tol)
        chk("S", "k", kept["k"], k - 1, cid, i, tol=0)
    F = sets["F"].get(cid)
    if F:
        af = a.get("F")
        chk("F", "excluded_set", af["excluded"] if af else None, F["exclude"], cid, tol=0)
        chk("F", "refused", af["refused"] if af else None, F["refused"], cid, tol=0)
        if not F["refused"] and af and af["kept"]:
            r = refits[("F", cid)]
            for aq, _, rq, tol in MAP:
                chk("F", aq, af["kept"][aq], r[rq], cid, None, tol)
            chk("F", "k", af["kept"]["k"], r["k"], cid, tol=0)
    elif "F" in a:
        chk("F", "unexpected_flag_button", True, False, cid, tol=0)
    want = [s for s in sets["R"] if s["id"] == cid]
    chk("R", "replicates", len(a["R"]), len(want), cid, tol=0)
    for s, ar in zip(want, a["R"]):
        chk("R", "excluded_set", ar["excluded"], s["exclude"], cid, s["rep"], tol=0)
        r = refits[("R%d" % s["rep"], cid)]
        for aq, _, rq, tol in MAP:
            chk("R", aq, ar["kept"][aq], r[rq], cid, s["rep"], tol)
        chk("R", "k", ar["kept"]["k"], r["k"], cid, s["rep"], tol=0)
out = [f"[{label}] oracle: {env}; configurations with app output: {len(corpus) - len(missing)}/{len(corpus)}; missing/error: {missing}",
       "set | quantity | pass/checks | max normalized diff | tol"]
tot = {}
for (st, q), s in stats.items():
    out.append(f"{st} | {q} | {s['passes']}/{s['checks']} | {s['max']:.3e} | {s['tol']}")
    t = tot.setdefault(st, [0, 0]); t[0] += s["passes"]; t[1] += s["checks"]
for st, (ps, n) in tot.items():
    out.append(f"SET {st}: {ps}/{n} checks pass")
ps = sum(t[0] for t in tot.values()); n = sum(t[1] for t in tot.values())
out.append(f"E1 TOTAL {ps}/{n} checks pass; failures {len(fails)}")
txt = "\n".join(out); print(txt)
Path(f"e1_compare_{label}.txt").write_text(txt + "\n", encoding="utf-8")
Path(f"e1_failures_{label}.json").write_text(json.dumps(fails[:500], indent=1), encoding="utf-8")
sys.exit(0 if not fails and not missing else 1)
