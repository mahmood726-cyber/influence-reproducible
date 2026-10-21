# Equivalence of the archived influence snapshots with allmeta v1.8.0

allmeta v1.8.0: tag `v1.8.0`, commit `1cb3f8409c7af75ed41f7e1811f9c502f900fc79`, DOI 10.5281/zenodo.23515177.
It contains pull request #170 (`feat/influence-v2-exclude-repool`, merge `6702536`), the v2 exclusion / re-pool
feature this archive's v2 layer measures.

## 1. Which tier was validated at which commit

| Tier | Validated at allmeta commit | In allmeta release | Re-pinned to v1.8.0? |
|---|---|---|---|
| v1 primary comparison, 164,802/164,802 checks, 142 configurations | `c6b8912` (PR #108, the corrections); `app/` holds the `fd45b9f` page bytes (PR #109, Validate panel, numerical code unchanged) | v1.3.0, DOI 10.5281/zenodo.23330389 | **No.** `app/` is unchanged and the 164,802 checks remain a claim about `c6b8912`/`fd45b9f`, not about v1.8.0. |
| v2 app bit identity, 126,000/126,000 | `f96772b`, re-pinned and re-executed at `1cb3f84` | v1.8.0 | Yes |
| v2 E2, 96,650/96,650 | `f96772b`, re-pinned and re-executed at `1cb3f84` | v1.8.0 | Yes |
| v2 E1 (S 115,270 + F 1,080 + R 5,563 = 121,913) and the 494 fresh fits | `f96772b`, re-pinned and re-executed at `1cb3f84` | v1.8.0 | Yes |
| v2 E3, 31/31 scripts and 27,637/27,637 values, plus 3/3 planted failures | `f96772b`, re-pinned and re-executed at `1cb3f84` | v1.8.0 | Yes |

The two source commits in full: `c6b8912c951a107a04228b9b52004d7ecc0d20e5` (v1 engine) and
`f96772b37bc80c621a77871b428f3cb2e94f3354` (v2 captures). Both are ancestors of `1cb3f84`. `c6b8912` is first
released in allmeta v1.3.0; `f96772b` is first released in v1.8.0.

The v1 primary tier is **not** re-pinned because the engine it measured has since changed: between `c6b8912`
and `1cb3f84`, `shared/ma-core.js` gains a new global REML tau-squared search (+233/-1 lines) and
`influence/index.html` changes by +411/-47 lines. Those are ENGINE changes to the exact files the v1
comparison exercised, and this archive does not re-run the 164,802-check R validation, so no v1.8.0 claim is
made for them. Section 2 lists every such file.

## 2. Files under `influence/`, `shared/` and `hub/shared/` that differ between `c6b8912` and `1cb3f84`

223 files differ: 46 modified, 177 added, 0 deleted. 21 are ENGINE and 202 are NON-ENGINE.
**Classification rule:** ENGINE = code or pinned reference data whose value can enter a displayed or exported
number; NON-ENGINE = CSS, the build stamp, documentation, test specs/fixtures/pixel references, and UI-state
or export-rendering modules.

193 of the 223 are Playwright specs, fixtures and pixel references: 192 under `hub/shared/tests/` (166 added,
26 modified) and one modified under `shared/tests/` (`shared/tests/nma-multiarm-v1.spec.mjs`). All 193 are
NON-ENGINE and none is loaded by any page. The complete 223-file classification, including every one of those
paths, is in `v2/provenance/engine-scope-c6b8912.json`. The remaining 30 files are listed in full here.

| File | Change | Class | Loaded by `app/` page | Loaded by `v2/app/` page | Reason |
|---|---|---|---|---|---|
| `hub/shared/analysis-lifecycle.js` | added | NON-ENGINE | no | yes | run/stale badge lifecycle; UI state only |
| `hub/shared/chart-download.js` | modified | NON-ENGINE | no | no | chart export plumbing (lazy-loads the vendored jsPDF) |
| `hub/shared/csv-upload.js` | modified | ENGINE | yes | yes | CSV input parser; produces the numbers the engine consumes |
| `hub/shared/plot-export.js` | added | NON-ENGINE | no | yes | plot export UI |
| `hub/shared/results-export.js` | modified | NON-ENGINE | yes | yes | export-bar CSS only |
| `influence/README.md` | modified | NON-ENGINE | no | no | page documentation |
| `influence/index.html` | modified | ENGINE | yes | yes | the influence page itself (markup, computation, rendering) |
| `influence/influence-extra.js` | added | ENGINE | no | yes | the v2 exclusion / re-pool feature that E1 measures |
| `influence/r-script.js` | added | ENGINE | no | yes | generates the downloadable metafor script that E3 runs |
| `influence/validate/MANIFEST.json` | added | ENGINE | no | no | pinned corpus/reference manifest of the in-app Validate panel |
| `influence/validate/README.md` | added | NON-ENGINE | no | no | panel documentation |
| `influence/validate/adapter.js` | added | ENGINE | yes | yes | in-app Validate panel adapter |
| `influence/validate/corpus/corpus.json` | added | ENGINE | no | no | pinned validation corpus (reference input) |
| `influence/validate/corpus/reference.json` | added | ENGINE | no | no | pinned metafor reference values |
| `shared/alm-validate.js` | modified | ENGINE | yes | yes | in-app validation panel; computes check verdicts |
| `shared/build-info.js` | modified | NON-ENGINE | yes | yes | build stamp (version, commit, build time) |
| `shared/canonical-datasets.js` | modified | NON-ENGINE | yes | yes | example-dataset text helpers |
| `shared/cross-design.js` | modified | ENGINE | no | no | cross-design synthesis engine |
| `shared/dta-bivariate.js` | modified | ENGINE | no | no | DTA bivariate engine |
| `shared/effect-size-accuracy.js` | added | ENGINE | no | no | effect-size conversion engine |
| `shared/fragility.js` | modified | ENGINE | no | no | fragility-index engine |
| `shared/hero-examples.js` | modified | NON-ENGINE | yes | yes | example-dataset loader manifests |
| `shared/ma-comparisons-v1.js` | modified | ENGINE | no | no | pairwise comparison engine |
| `shared/ma-core.js` | modified | ENGINE | yes | yes | shared meta-analysis engine (the influence page's fitter) |
| `shared/multivariate-ma.js` | modified | ENGINE | no | no | multivariate meta-analysis engine |
| `shared/nma-multiarm-v1.js` | modified | ENGINE | no | no | multi-arm NMA engine |
| `shared/rve-extras.js` | added | ENGINE | no | no | robust variance estimation extras |
| `shared/rve.js` | modified | ENGINE | no | no | robust variance estimation engine |
| `shared/stats-qt.js` | modified | ENGINE | no | no | t / incomplete-beta quantile library |
| `shared/trimfill.js` | modified | ENGINE | no | no | trim-and-fill engine |

Five ENGINE files are loaded by the v1 `app/` page (`hub/shared/csv-upload.js`, `influence/index.html`,
`influence/validate/adapter.js`, `shared/alm-validate.js`, `shared/ma-core.js`); seven are loaded by the
`v2/app/` page (those five plus `influence/influence-extra.js` and `influence/r-script.js`). Neither
`shared/stats-qt.js`, `shared/rve.js` nor `shared/multivariate-ma.js` is requested by the influence page:
the page's 24 `src`/`href` assets do not reference them, none of those 24 files references them, and the only
dynamic script loads in the dependency set are the vendored jsPDF (`hub/shared/plot-export.js`) and
`shared/webr-runner.js` (`shared/alm-validate.js`), which is itself byte-identical at `1cb3f84`.

## 3. The `v2/app/` snapshot re-pin

Before the re-pin, `v2/app/` was the restricted git-archive export of `f96772b` taken on Windows: 399 of its
437 files were the exact Git blob and the other 38 carried CRLF where the blob carries LF. After CRLF-to-LF
normalization **all 437 files were identical to `f96772b`**, which confirms the snapshot's stated provenance.

Against `1cb3f84` the same 437 files split as:

| State before the re-pin | Files |
|---|---:|
| byte-identical to the `1cb3f84` blob | 379 |
| identical after CRLF-to-LF normalization only | 38 |
| content differs | 20 |
| absent from v1.8.0 | 0 |

All 58 raw-differing files were replaced with their exact `1cb3f84` blob bytes, and `v2/app/app-sha256.json`
was regenerated over the 437 files. `v2/app/` is now byte-for-byte the `1cb3f84` blob set; no file is
deliberately kept modified. The complete 437-file table is in `v2/provenance/repin-v1.8.0.json`; the 38
line-ending-only paths are listed there as well.

The 20 content differences were:

| File | Class | Loaded by the page | Difference from v1.8.0 |
|---|---|---|---|
| `shared/ma-core.js` | ENGINE | yes | v1.8.0 adds a Q-based `I2` when `method === "FE"`; the REML paths are unchanged |
| `hub/shared/analysis-lifecycle.js` | NON-ENGINE | yes | v1.8.0 also tracks the last *attempted* run, so re-committing an input that has already been run no longer marks the result stale |
| `hub/shared/results-export.js` | NON-ENGINE | yes | v1.8.0 adds `flex-wrap:wrap;max-width:100%` to the export-bar CSS |
| `shared/build-info.js` | NON-ENGINE | yes | v1.8.0 build stamp (`v1.7.0`/`7899ce5` to `v1.8.0`/`42a94da`, new build time) |
| `shared/canonical-datasets.js` | NON-ENGINE | yes | v1.8.0 adds `toEffectSeLabelText`; no existing function changed |
| `shared/hero-examples.js` | NON-ENGINE | yes | v1.8.0 adds the `effect-se-label` example manifest and its switch case |
| `shared/stats-qt.js` | ENGINE | no | v1.8.0 tightens `_betacf` (`MAXIT` 200 to 1000, `EPS` 3e-7 to 4e-15) and adds NaN guards to `pt`/`qt` |
| `shared/rve.js` | ENGINE | no | v1.8.0 replaces the Gauss-Jordan inverse with partial-pivot LU plus a reciprocal-condition guard |
| `shared/multivariate-ma.js` | ENGINE | no | v1.8.0 adds a REML score / Fisher-information polish and a Nelder-Mead convergence break |
| `hub/shared/tests/component-nma-parity.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/cumulative-subgroup-pi.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/cumulative-subgroup-qb.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/cumulative-subgroup-sanity.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/gosh-plus.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/limit-ma-plus.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/multivariate-ma-parity.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/nma-inconsistency-dom.cjs` | NON-ENGINE | no | Playwright DOM helper |
| `hub/shared/tests/playwright.pixels.config.mjs` | NON-ENGINE | no | Playwright configuration |
| `hub/shared/tests/validate-integration.spec.mjs` | NON-ENGINE | no | Playwright spec |
| `hub/shared/tests/validation-fixture.mjs` | NON-ENGINE | no | Playwright fixture |

One ENGINE change (`shared/ma-core.js`) is loaded by the page, so the equivalence of the v2 tiers is
established by execution, not by byte comparison alone.

## 4. Equivalence by execution on the v1.8.0 bytes

Re-run on 21 Oct 2026 on Windows 11, Node v24.16.0, Playwright 1.59.1 (Node) and 1.60.0 (Python),
Chrome 155.0.8059.85, R 4.6.0, metafor 5.2.1, metadat 1.6.0, jsonlite 2.0.0, digest 0.6.39.

### 4.1 Page capture (app bit identity and E2 input)

`bench/runner.cjs` (the archive's historical browser extractor, with its `<PLAYWRIGHT_MODULE>` placeholder
resolved as `bench/README.md` directs) was run over all 142 configurations of `data/corpus.json`, first
against the original `f96772b` snapshot bytes and then against the re-pinned `1cb3f84` bytes.

- Both runs reported `APP 142 configurations; 0 page errors`.
- The two raw runner outputs are byte-identical to each other: SHA-256
  `9313b4579c36fc32ef17c65c9b78e286dec1310e8d03fc2f856683354e659a2c`.
- Re-serialized with the archive's own `json.dumps` default separators, each run is **byte-identical to the
  archived `v2/captures/cap_f96772b.json`**: SHA-256
  `6b486c14d36bc7b317dd022f81bc26ccf7d1a2f994763a133806e852783a573c`.

Running the bit-identity tier on the fresh `1cb3f84` capture gives `V2 BIT IDENTITY 126000/126000`, and
`v2/tools/e2_compare.py` on it gives `E2 TOTAL 96650/96650 checks pass`.

### 4.2 Exclusion-UI capture (E1 input)

`v2/tools/e1_harness.py` was run against the re-pinned `v2/app/` and reported
`E1APP 142 configurations; 0 page errors; 0 configuration errors`. Its output is **byte-identical to the
archived `v2/captures/e1app_f96772b.json`**: SHA-256
`ac996952fa179639626c6b6d508fc06058637739e3de96626d217d32ca45fecb`.

`v2/tools/e1_compare.py` on that fresh capture, against 494 fresh metafor 5.2.1 fits, gives
`SET S: 115270/115270`, `SET F: 1080/1080`, `SET R: 5563/5563`, `E1 TOTAL 121913/121913 checks pass; failures 0`.

### 4.3 Downloaded R scripts (E3)

`v2/tools/gen_scripts.py` was run against the re-pinned `v2/app/` and regenerated all 34 scripts
(31 sampled plus 3 planted) with 0 page errors. For all 34, **the script body from line 3 onward is
byte-identical to the archived `v2/e3_scripts/` file**. Only the two provenance comment lines differ:

```
line 1  archived:  # Influence diagnostics: R reproduction script generated by allmeta influence v1.7.0.
line 1  v1.8.0  :  # Influence diagnostics: R reproduction script generated by allmeta influence v1.8.0.
line 2             # Generated <wall-clock timestamp>. Tested with R 4.6.0 and metafor 5.2-1.
```

Line 1 is the build stamp and line 2 is the generation time; both are comments and neither enters the
27,637 compared values. The regenerated scripts were then executed unmodified under Rscript with the
archive's own pass rule: 31/31 scripts exit 0 with their exact pre-registered `ALL n/n app values reproduced`
denominators, 27,637/27,637 values, and the 3 planted controls still exit 1 reporting exactly one value
failure. `v2/e3_scripts/` keeps its original pre-registered bytes; it is archive evidence, not an allmeta
path, so it is not re-pinned.

### 4.4 The archive's own v2 command on the re-pinned tree

`INFLUENCE_V2_ONLY=1 Rscript validate.R` from the archive root, on the re-pinned tree, in 311.1 s:

```
V2 INPUT SHA256 516/516
V2 APP SHA256 437/437
V2 PREREG SHA256 3/3
V2 BIT IDENTITY 126000/126000
E2 TOTAL 96650/96650 checks pass
V2 FRESH REFITS 494/494 | max normalized diff 0 | tolerance 1e-12
SET S: 115270/115270 checks pass
SET F: 1080/1080 checks pass
SET R: 5563/5563 checks pass
E1 TOTAL 121913/121913 checks pass; failures 0
V2 E3 SCRIPTS 31/31
V2 E3 VALUES 27637/27637
V2 E3 PLANTED 3/3 expected failures
V2 REPRODUCED
```

Every v2 count equals the archived and paper count exactly. The 494 stored/fresh fit comparison reports a
maximum normalized difference of 0. The run's own `outputs/v2/fresh_refits.jsonl` reproduced the archived
file line for line: of its 496 lines, all are identical once the per-fit `sec` wall-clock field is dropped,
and no other field differs on any line. `outputs/v2/e1_compare_fresh.txt`, `outputs/v2/e2_compare_fresh.txt`,
`outputs/v2/refit.log` and both comparator logs came back byte-identical to the archived copies. The only
other run artefacts that changed were the 34 `outputs/v2/e3/*/influence-plots.pdf` files (PDF creation
timestamp) and the `seconds` fields of `outputs/v2/e3_results.json`; `outputs/` is excluded from the release
inventory and its archived copies are left in place.

## 5. What was not run

The default `Rscript validate.R` (v1 followed by v2) was **not run**. Its v1 half is the 164,802-check refit,
historically measured at 475 minutes, and this lane did not execute it. The v1 R references do not depend on
the app, and the v1 `app/` snapshot is unchanged by this release, so nothing in the v1 tier is affected by the
re-pin; equally, no new v1 evidence is produced here and the v1 tier's 164,802 checks remain a claim about
`c6b8912`/`fd45b9f`, not about v1.8.0. The manager must still run the complete default validation before
release.

No Playwright pixel or accessibility suite from `v2/app/hub/shared/tests/` was run; those specs are allmeta's
own and are not part of this archive's contract.

## 6. Conclusion

All four v2 tiers — app bit identity 126,000/126,000, E2 96,650/96,650, E1 121,913/121,913 with 494/494 fresh
fits, and E3 31/31 scripts with 27,637/27,637 values plus 3/3 planted failures — hold unchanged on the
allmeta v1.8.0 bytes, established by re-executing every browser capture, replay and comparator the archive
documents and obtaining byte-identical captures. The v1 primary tier's 164,802 checks remain scoped to
allmeta `c6b8912` (page bytes `fd45b9f`) and are not claimed for v1.8.0.
