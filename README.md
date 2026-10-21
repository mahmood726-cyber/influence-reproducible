# Version 1.1.0 — paper 11 extension (local, unpublished)

New in 1.1.0: the separate `v2/` layer archives the influence page, E2's 96,650 comparisons, E1's 121,913 exclusion checks (including 494 fresh metafor 5.2.1 fits), and 31 downloaded R scripts reproducing 27,637 values plus three expected failures. New DOI: **[ARCHIVE v1.1.0 DOI PENDING]**.

The `v2/app/` snapshot is pinned to the allmeta release **v1.8.0** (tag `v1.8.0`, commit `1cb3f8409c7af75ed41f7e1811f9c502f900fc79`, DOI **10.5281/zenodo.23515177**), which contains pull request #170, the exclusion/re-pool feature the v2 layer measures; its 437 files are byte-for-byte the v1.8.0 Git blobs. The historical captures were taken at `f96772b`, an ancestor of v1.8.0, and re-running every documented capture, replay and comparator on the v1.8.0 bytes reproduces them byte-identically with every v2 count unchanged. The v1 primary tier's 164,802 checks stay scoped to allmeta `c6b8912` (page bytes `fd45b9f`, allmeta v1.3.0) and are **not** claimed for v1.8.0. [RELEASE_EQUIVALENCE.md](RELEASE_EQUIVALENCE.md) records which tier was validated at which commit, every `influence/`/`shared/`/`hub/shared/` file that differs between `c6b8912` and `1cb3f84` classified ENGINE or NON-ENGINE, the 437-file snapshot table, and the execution check with full SHA-256 values and counts.

From this archive root, run **`Rscript validate.R`** with R 4.6.0, metafor 5.2.1, metadat 1.6.0, jsonlite 2.0.0, digest 0.6.39, and Python 3.13 or later on PATH (standard library only). The default runs v1 and then v2. Budget several hours for v1 (historical measurement: 475 minutes; the new two-R-process cap may increase this) plus v2 (measured 4.6 minutes here; allow 5–15 minutes on comparable hardware). `INFLUENCE_V2_ONLY=1` skips the long v1 refit. A full success ends with `V2 REPRODUCED`; any failure exits nonzero. This lane tested v2 only; the manager must run the complete default validation before release.

See [v2/README.md](v2/README.md) for tier definitions, source dependencies, version gates, exact expected counts, fresh-fit tolerance and logs. E2 and E1-S reuse the archived leave1out references and are not independent evidence. E1-F/R and E3 execute R afresh. All browser captures are historical evidence; the command does not launch a browser.

The existing v1 statistical evidence, input hashes, expected counts, validation function body and app snapshot remain unchanged. Only this README, CHANGELOG, CITATION, release metadata, the validation entrypoint and the release-wide source inventory are updated; their exact v1 originals are in `v2/provenance/v1-release/`. The original worker helper remains pinned and unchanged; the entrypoint reduces its worker count in memory to keep at most two R processes. The historical documentation below describes v1, including its old three-worker scheduling and then-undisplayed fields. The v1 `analysis/verify_archive.py` remains unchanged and expects metadata version 1.0.0; use `python v2/tools/verify_release.py` for the 1.1.0 inventory and preservation checks. `analysis/verify_archive.py` also asserts that no source file contains a Windows drive-letter user or project path, and 21 files of the captured `v2/app/` snapshot do: 20 Playwright sanity specs carry one in a `cd` usage comment and `v2/app/hub/.gitignore` cites one in a comment. Those are allmeta's own bytes, identical at `f96772b` and `1cb3f84`, and the snapshot is pinned to them, so they are reported rather than edited; `v2/tools/verify_release.py` is the verifier for the 1.1.0 tree.

---

# Influence diagnostics for meta-analysis in the browser

This archive validates allmeta's intercept-only REML influence-diagnostics page against metafor. The complete primary comparison passes **164,802 of 164,802 checks after three fixes**, across **142 configurations**, **113 of 114 enumerated metadat datasets**, and **9,594 effect rows**. Rows across configurations are numerical test inputs, not independent studies or participants.

Allmeta commits: `c6b8912` (PR #108, the corrections; numerical engine validated here) and `fd45b9f` (PR #109, adds the in-app Validate-in-R panel; numerical code unchanged). Both are in allmeta v1.3.0, https://doi.org/10.5281/zenodo.23330389. The archived page in app/ is the `fd45b9f` version. `app/app-sha256.json` identifies the exact archived bytes; `SOURCE_SHA256.json` covers archive sources. No release certification or deployment is implied.

## Validate with one command

Use R **4.6.0**, metafor **5.2-1**, metadat **1.6-0**, and installed `jsonlite` and `digest`. Set `R_LIBS_USER` / `R_LIBS` to your package libraries if needed. From this archive's root:

```sh
Rscript validate.R   # standard R 4.6.0: about 8 hours (measured 475 min); the 1,653-study configuration dominates
```

The command SHA-256-verifies its source data, app results and fitting helpers against `INPUT_SHA256.json` before fitting. It enforces unique keys, exact configuration coverage, required fields, valid types and vector cardinality. It calls `rma(method="REML")`, `leave1out`, `influence`, `baujat`, and `radial(rma(method="FE"))` for every configuration and compares fresh R values with `results/app-patched.json`. It prints per-quantity totals, writes `outputs/validate_R_table.csv`, and exits nonzero for any failure or incomplete coverage. It should end with `164802/164802 checks pass`.

The validator prioritizes `R_LIBS_USER` over `R_LIBS` and checks the exact paper R/metafor/metadat versions before fitting. This matters when an older metafor is installed alongside jsonlite in another library. For configurations with at least 500 rows, three local R workers compute the distinct deletion fits in new `.validate-work/` directories, using the source run's fit arguments and exact cache keys. Each worker uses one BLAS thread. Completed chunks are published atomically, checked for input identity and unique/exact deletion coverage, then reused by the diagnostic calls. No historical checkpoint is read. Worker errors or a six-hour worker bound fail the run; temporary worker logs remain available for diagnosis.

**Replayed rather than recomputed in R:** one archived table-row count and four archived nonempty-plot checks per configuration (710 checks). Statistical quantities and influential flags are recomputed. The browser's Tier 2 independently runs all page calculations and renders all configurations against the pinned reference; it does not load saved app outputs. Fresh R runs do not reuse historical fit checkpoints. Exact duplicate deletion fits within each fresh configuration are reused between metafor diagnostic calls by the source run's verified cache wrapper.

The two largest configurations require many dense matrix products. The source run used a local R 4.6.0 runtime with the installed SciPy OpenBLAS DLL: only PE exported-symbol aliases/order changed, with no change to numerical machine code or metafor. `results/blas-provenance.json` records source/modified SHA-256 and all aliases. Standard R versus accelerated R: **19,879/19,879 numeric checks**, **29 configurations**, maximum normalized difference **1.177090768607161e-10**, tolerance **1e-9**. Cache/file-worker parity: **32,928/32,928 checks**, **78 configurations**, maximum difference **0**. See the corresponding verification JSON files and `bench/` scripts. Standard R is supported but can be much slower. No runtime is downloaded or installed by the validator.

The reference tightens convergence to `threshold=1e-12*max(1,starting_tau2)`, `maxiter=10000`, `stepadj=1`. An independent scalar score supplies only starting values through supported control/code2 interfaces. Metafor still performs its own REML iteration and likelihood checks; no variance is frozen. The validator follows that policy. Set `OPENBLAS_NUM_THREADS=2` with the accelerated runtime if desired.

## Rebuild tables and figures

Use Python 3.13 and the package versions in `analysis/requirements.txt` (the measured environment is recorded in `analysis/environment.json`). Exact image regeneration and the historical maxima audit should use this environment; Python's summation and rendering-library changes can otherwise alter bytes or last-bit differences. With these packages installed:

```sh
python analysis/make_outputs.py
python analysis/verify_archive.py
python -m pytest analysis/test_safeguards.py -q -p no:cacheprovider
```

`make_outputs.py` recomputes both comparison ledgers from the recorded input/reference/app values, checks the original per-quantity summaries, and generates Table 1 by quantity, Table 2 by configuration, Figure 2, the visual abstract, image sizes, source-linked numbers, and a reproduction report. Figures are 170 mm wide, 300 dpi, with text at least 8 pt. `expected/paper_values.json` is an assertion contract, never a replacement for computed values. `verify_archive.py` checks source and app hashes, asset availability, tables, image dimensions/pixels and deterministic regeneration; it permits a future `.git` directory.

Serve `app/` as a static root and open `/influence/index.html` to run the page. All resources requested by the page, corpus replay, and live R check are included byte-for-byte from the worktree, including the pinned webR binaries/packages and lazy VFS resources. `app/request-assets.json` records observed same-origin paths. Navigation to other allmeta tools and external evidence links is outside this standalone page snapshot. On `file://`, the replay accepts the two manifest-listed corpus JSON files through its picker; live R requires HTTP(S).

## What is compared

The full fit: mean, SE, tau-squared, Q, df, sum of random-effects weights and every raw weight. Each row: LOO mean/SE/normal 95% CI, deleted studentized residual, DFFITS, Cook's D, covariance ratio, hat, influential flag, normalized weight, REML Baujat x/y, and FE radial x/z/residual; plus radial slope and the UI checks above.

The normalized difference is `abs(App-R)/max(1,abs(R))`. REML-dependent quantities use **1e-6**; Q/df and FE radial quantities use **1e-9**; flags and UI contracts require exact equality. Only explicit null on both sides can represent a genuinely undefined deletion quantity. Missing keys, NaN, infinity and wrong types fail; the primary source corpus has no null numerical values.

## Three defects and differing denominators

1. **DFFITS:** the denominator omitted `sqrt(hat_i)`. Adding it changed the DFFITS comparisons from **0/9,594** to **9,594/9,594**.
2. **Influential flags:** the old Cook's D/hat/residual heuristic differed from metafor. The corrected rule uses `abs(DFFITS)>3/sqrt(k-1)`, Cook's D above the median chi-square(1), hat above `3/k`, or `abs(DFBETAS)>1`. Flags changed from **9,255/9,594** to **9,594/9,594**, consistently in the table and plot.
3. **Baujat estimator:** the shared plot defaulted to DL although the page fit REML. The page now requests REML while other callers retain DL by default. REML x changed from **292/9,594** to **9,594/9,594**, and y from **636/9,594** to **9,594/9,594**. The horizontal label now identifies the squared Pearson residual.

Before: **155,797/183,990**; after: **164,802/164,802**. The before denominator included **19,188 additional DL Baujat control comparisons**, all of which passed; they demonstrated the estimator mismatch. Those extra controls are not part of the primary after-fix contract. Table 1 retains separate before/after check-count columns and explicitly labels DL-only rows.

## Corpus and limits

`bench/build_corpus.R` enumerates `data(package="metadat")` and evaluates the installed documentation's preparation/escalc recipes; `supplements.R` supplies documented alternate columns and standard transformations. For each dataset/effect definition, the first recipe with the largest eligible row count is retained. Identical stored yi/vi aliases of named measures are deduplicated. Only finite effects and strictly positive finite variances enter both engines. Retained/omitted source-row positions and preparation errors/warnings are archived. `dat.metap` is excluded because it supplies p-values without the required effect/variance ingredients. Package documentation remains in `bench/documentation/`.

This is an **intercept-only REML** model, with no estimator selector or HKSJ adjustment. The page does not expose or compare **tau2.del/QE.del, LOO p/I2/Q, or full-model p/I2**; LOO tau-squared is also outside the displayed comparison. These reference fields are retained but not credited as successful checks. **GOSH is only a link**. Some configurations ignore dependence: single-arm logits from network/arm data, arms 1–2 from multi-arm data, or MD summaries of participant-level recurrence data. They test arithmetic under the supplied model and do not endorse clinical pooling or independence assumptions.

Live webR uses **metafor 4.8-0** (webR **0.5.5**, R **4.5.1**), distinct from paper metafor **5.2-1**. Both versions appear in the validation panel. The in-app reference is hash-pinned evidence; it is not a fresh R execution. No paper DOI or archive publication is invented.

| Item | Static or dynamic | Source / validation |
|---|---|---|
| Source corpus/reference/app outputs | Static recorded evidence | SHA-256 pins, original provenance and comparison ledgers |
| Versions, tolerances, expected totals | Static protocol/assertions | Source scripts, expected/paper_values.json |
| Regenerated comparisons, tables, figure coordinates | Dynamic | Strict comparison of archived real inputs/outputs |
| Fresh R fits | Dynamic | validate.R, actual metafor calls |
| UI checks in R | Archived replay | Explicit Mode column; browser replay tests render afresh |
| Formatting, dimensions, colours | Static presentation | make_outputs.py and image verification |
| allmeta merged commits | Static provenance | `c6b8912` (corrections), `fd45b9f` (Validate panel); exact app bytes separately hashed |

Derived from [allmeta](https://github.com/mahmood726-cyber/allmeta) and allmeta v1.2.1 DOI **10.5281/zenodo.23288388**, both recorded as `isDerivedFrom`. Supplied identifiers are metadata; no new scientific identifiers are invented. MIT covers this archive's code; package/data documentation and vendored runtime assets retain their upstream rights and licences. No manuscript drafts or local machine paths are distributed.
