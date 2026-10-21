import json, random, sys
from pathlib import Path
A = Path(__file__).resolve().parents[2]
c = json.loads((A/"data"/"corpus.json").read_text(encoding="utf-8"))
r = json.loads((A/"results"/"reference.json").read_text(encoding="utf-8"))
ids = sorted(c)
F, R = {}, []
for i in ids:
    k = len(c[i]["yi"]); fl = [j for j, f in enumerate(r[i]["flags"]) if f]
    if fl: F[i] = {"exclude": fl, "k": k, "refused": k - len(fl) < 3}
rng = random.Random(20261021)
for i in ids:
    k = len(c[i]["yi"])
    if k > 500: continue
    m = max(1, k // 5)
    for rep in (1, 2, 3):
        R.append({"id": i, "rep": rep, "k": k, "exclude": sorted(rng.sample(range(k), m))})
rng3 = random.Random(20261022)
strata = [(4, 10), (11, 50), (51, 500)]
E3 = []
for lo, hi in strata:
    E3 += rng3.sample([i for i in ids if lo <= len(c[i]["yi"]) <= hi], 10)
E3.append("dat.bcg::RR")
out = {"F": F, "R": R, "E3": E3}
Path(sys.argv[1]).write_text(json.dumps(out, indent=0), encoding="utf-8")
print("F", len(F), "refused", sum(v["refused"] for v in F.values()), "R", len(R), "E3", len(E3), len(set(E3)))
