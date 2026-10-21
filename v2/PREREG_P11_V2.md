# Pre-registration: influence v2 (paper 11 upgrade) exclusion re-fits, LOO-table crediting, R-script sample

Written Mon 19 Oct 2026, BEFORE any new R reference was generated. The sha256 of this file and of the
derived set file are recorded in PREREG_SHA256.txt at the time of writing; any later edit invalidates them.

Corpus: influence-reproducible v1.0.0 `data/corpus.json` (142 configurations, 9,594 rows), reference
`results/reference.json` (metafor 5.2-1, R 4.6.0). Row index i refers to position in corpus `yi`.

## Oracle
metafor 5.2-1 (pinned library on node `laptop`; fallback: node `baseimage`, system metafor 5.2.1).
`packageVersion("metafor")` is recorded in every output. Local metafor 5.0.1 is NOT used as oracle.
Fit: `rma(yi[keep], vi[keep], method="REML", test="z", control=ctl)` with the archive policy:
`ctl=list(threshold=1e-12, maxiter=10000, stepadj=1)`, `ctl$tau2.init <- start_tau(y,v)` (archive bench/starts.R),
`ctl$threshold <- 1e-12*max(1, ctl$tau2.init)`.
Recorded per fit: k, coef, se, zval, pval, ci.lb, ci.ub, tau2, I2, H2, QE, QEp.

## E1 exclusion sets (app: tick the per-study "Exclude" checkboxes, read the before/after panel)
- Set S (single exclusion; no new R): every row of all 142 configurations (9,594 exclusions). The re-pooled
  values must equal the archived metafor 5.2-1 `leave1out` row: estimate, se, ci.lb, ci.ub, zval, pval, tau2,
  I2, H2, Q, Qp, and k = k_full - 1.
- Set F (exclude all metafor-flagged studies): every configuration whose reference `flags` (influence()$is.infl)
  has >= 1 TRUE; excluded = all flagged rows; included only if k - |F| >= 3 (refused otherwise, and the
  refusal itself is a check). Expected 78 configurations. In the app this is the "Exclude all flagged" button;
  the app's flags equal the reference flags (archived 9,594/9,594), and the test asserts the excluded index set
  equals the reference flagged set before comparing numbers.
- Set R (random multi-exclusion): every configuration with k <= 500 (139), 3 replicate subsets each, size
  m = max(1, floor(k/5)) rows, drawn by Python `random.Random(20261021)`, iterating configurations in sorted id
  order and replicates 1..3, `rng.sample(range(k), m)` sorted. Expected 417 fits. All keep >= 3 rows (k >= 4).
- Quantities compared: mu, se, ci.lb, ci.ub, zval, pval, tau2, I2, H2 at normalized tolerance 1e-6;
  QE and QEp at 1e-9; k exact. Normalized difference = |app - R| / max(1, |R|) (archive rule).
  Explicit null only matches explicit null.

## E2 (already-archived references, no new R)
Credit, for every row: loo tau2, I2, H2, Q, Qp, zval, pval; inf tau2.del, QE.del; dfbetas intrcpt; and per
configuration full ciLo, ciHi, p, I2, Qp. Tolerances: Q, Qp, QE.del 1e-9; all others 1e-6 (REML-dependent).
Expected checks: 10 x 9,594 + 5 x 142 = 96,650.

## E3 R-script sample
30 configurations: 10 drawn from each k stratum [4,10], [11,50], [51,500] with `random.Random(20261022)`
(`rng.sample(sorted ids in stratum, 10)`, strata in that order), plus `dat.bcg::RR`. For each, the script
downloaded from the page is run unmodified with Rscript under metafor 5.2-1; it must print its own
"ALL n/n app values reproduced" line and exit 0. Planted control: for 3 of those scripts (the first of each
stratum) one embedded app value (full.mu) is perturbed by +1e-3; each must FAIL (non-zero exit, FAIL line).

## Comparators must fail first
Each comparator is run on a planted defect (tau2 x (1+1e-4); one k off by one; one flag flipped) and must
report failures before its pass counts are believed.

## Final regression
Archive harness (p11work harness.py port of bench/runner.cjs + archive bench/compare.py) on the final commit
must give 164802/164802; in-app "Replay published corpus" must give 164802/164802.
