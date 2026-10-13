# Influence diagnostics validation


Source commit: `6036f3b6c1fd404b6da7916460faa8b3ebaf56bc`. Source repository was read-only; all work and the proposed patch are in this job directory.

Actual corpus: **142 configurations, 113/114 metadat datasets, 9594 effect rows across configurations**. These rows are numerical test inputs, not a claim of independent studies or a pooled scientific finding.

Reference completed: **142/142 configurations**. Missing: []. Runtime: R version 4.6.0 (2026-04-24 ucrt); metafor 5.2.1; metadat 1.6.0.

## Results

Verbatim final lines from the comparison runs:

```text
155797/183990 checks pass
164802/164802 checks pass
```

Original totals include the additional DL Baujat control comparisons; patched totals use the intended REML Baujat comparison only. They therefore have different denominators. Boolean flags are checked exactly.

| Quantity | Original pass/checks | Original max difference | Patched pass/checks | Patched max difference | Tolerance |
|---|---:|---:|---:|---:|---:|
| full.mu | 142/142 | 1.9123525842793258e-15 | 142/142 | 1.9123525842793258e-15 | 1e-06 |
| full.seMu | 142/142 | 1.4849232954361469e-15 | 142/142 | 1.4849232954361469e-15 | 1e-06 |
| full.tau2 | 142/142 | 2.4424906541753444e-15 | 142/142 | 2.4424906541753444e-15 | 1e-06 |
| full.Q | 142/142 | 4.0972864014094276e-15 | 142/142 | 4.0972864014094276e-15 | 1e-09 |
| full.df | 142/142 | 0 | 142/142 | 0 | 1e-09 |
| full.swRE | 142/142 | 3.6796865982159471e-13 | 142/142 | 3.6796865982159471e-13 | 1e-06 |
| full.wRE | 9594/9594 | 4.9523238690315795e-13 | 9594/9594 | 4.9523238690315795e-13 | 1e-06 |
| loo_mu | 9594/9594 | 1.1707648739367471e-14 | 9594/9594 | 1.1707648739367471e-14 | 1e-06 |
| loo_seMu | 9594/9594 | 9.5505200969903115e-15 | 9594/9594 | 9.5505200969903115e-15 | 1e-06 |
| loo.ci.lb | 9594/9594 | 1.1018963519404679e-14 | 9594/9594 | 1.1018963519404679e-14 | 1e-06 |
| loo.ci.ub | 9594/9594 | 3.0427049768633196e-14 | 9594/9594 | 3.0427049768633196e-14 | 1e-06 |
| resid | 9594/9594 | 1.1923394866210988e-12 | 9594/9594 | 1.1923394866210988e-12 | 1e-06 |
| dffits | 0/9594 | 0.87984288985692383 | 9594/9594 | 3.129219106057235e-12 | 1e-06 |
| cooksD | 9594/9594 | 1.9259038808172591e-12 | 9594/9594 | 1.9259038808172591e-12 | 1e-06 |
| covRatio | 9594/9594 | 4.4465542359262145e-12 | 9594/9594 | 4.4465542359262145e-12 | 1e-06 |
| hat | 9594/9594 | 3.1141755840735641e-14 | 9594/9594 | 3.1141755840735641e-14 | 1e-06 |
| flags | 9255/9594 | 1 | 9594/9594 | 0 | 0 |
| weight.percent | 9594/9594 | 1.5445621194298185e-13 | 9594/9594 | 1.5445621194298185e-13 | 1e-06 |
| baujat.REML.x | 292/9594 | 4.6995976641051627 | 9594/9594 | 2.7505710987040211e-13 | 1e-06 |
| baujat.DL.x | 9594/9594 | 4.7906717969540994e-14 | not repeated | not repeated | 1e-09 |
| baujat.REML.y | 636/9594 | 5.7692772219097801 | 9594/9594 | 2.2911117447677043e-12 | 1e-06 |
| baujat.DL.y | 9594/9594 | 8.9661611468727642e-13 | not repeated | not repeated | 1e-09 |
| radial.x | 9594/9594 | 0 | 9594/9594 | 0 | 1e-09 |
| radial.z | 9594/9594 | 0 | 9594/9594 | 0 | 1e-09 |
| radial.resid | 9594/9594 | 4.8739402457862186e-14 | 9594/9594 | 4.8739402457862186e-14 | 1e-09 |
| radial.slope | 142/142 | 8.713907727914139e-16 | 142/142 | 8.713907727914139e-16 | 1e-09 |
| ui.table_rows | 142/142 | 0 | 142/142 | 0 | 0 |
| ui.plot_nonempty | 568/568 | 0 | 568/568 | 0 | 0 |

Differences are abs(app−R)/max(1,abs(R)); flags use 0/1 disagreement. Closed-form Q and fixed-effect radial quantities use 1e−9. REML-dependent estimates, SEs, CI endpoints, tau-squared, influence measures, and coordinates use 1e−6. No flat-likelihood relaxation was used. There are no exposed app p-values to compare.

## Actual app contract

The minimum is k=3. The main model is an intercept-only REML random-effects inverse-variance fit, with ordinary normal-theory SEs and z=1.959963984540054 for the plotted 95% LOO intervals. There is no method selector and no Hartung–Knapp adjustment.

The visible table contains effect, externally standardized deleted residual, hat, Cook’s D, DFFITS, covariance ratio, and LOO mean (SE). Internal full-fit output contains mean, SE, tau-squared, Q, df, unnormalized random-effects weights, and their sum. Raw weights and their sum are independently checked as 1/(vi + R tau-squared) and its sum, using the saved R fit and corpus variances. Weight percentages in this audit are normalized from those actual weights, not a visible table column. CI endpoints are the exact arithmetic used by the plotted LOO forest.

The app does **not** expose full-model p or I²; LOO p, tau-squared, I², or Q; or the influence tau2.del/QE.del columns. They are retained in reference.json but are not counted as successful app checks. GOSH is only a navigation link, not a calculation in this page. Radial output is the fixed-effect Galbraith construction (1/SE, yi/SE, fixed-effect slope, and residual from that line), checked against the returned coordinates of metafor::radial(rma(...,method="FE")) and the fixed-effect slope.

## Failures and minimal patch

1. `influence/index.html:241`: DFFITS divides the full-minus-deleted mean by sqrt(vi+tau2_deleted), omitting sqrt(hat_i). Metafor uses sqrt(hat_i*(vi+tau2_deleted)) for this intercept-only z-test model. The deleted residual, Cook’s D, and covariance-ratio formulas themselves are correct.

2. `influence/index.html:257` and `:367`: the table and plot flag Cook’s D>1 OR hat>3/k OR |rstudent|>2. This does not match `influence(res)$is.infl`, despite the footer claim at line 155. Metafor flags |DFFITS|>3/sqrt(k−1), Cook’s D>qchisq(.5,1), hat>3/k, or |DFBETAS|>1. The patch computes the intercept-only DFBETAS using the full design at the deleted tau-squared and applies the same rule to table and plot.

3. `influence/index.html:281` calls `shared/diagnostic-plots.js:31`, which unconditionally uses DL. Its coordinates match a **DL** metafor Baujat fit, not the page’s REML main model. The patch adds an optional estimator argument (leaving other callers’ DL default intact) and passes REML from this page. It also changes the horizontal label from contribution to Q to squared Pearson residual, matching what the random-effects Baujat coordinate represents.

`fix.patch` is a unified diff against allmeta; it is not applied to the source repository. `patched/` contains the reviewed candidate. Full per-check failures are in failures-original.json and failures-patched.json. The existing orientation Python test checks stored R values against R; this audit instead drove the shipped page itself in Chrome.

## Corpus and provenance

Candidates were enumerated with data(package="metadat"), not a hand-picked list. Installed Rd examples and descriptions are in documentation/. build_corpus.R evaluates preparation and escalc recipes; supplements.R maps alternate documented columns and standard escalc transformations. Each saved dataset/definition has one configuration: the first recipe with the largest eligible row count for that definition. Stored yi/vi aliases identical to a documented named measure are deduplicated. Only finite effects and strictly positive finite variances enter both engines; each configuration records retained row positions and removed positions. Preparation-expression errors and warnings are preserved in corpus-audit.json.

Alternate benchmark definitions are explicit in configurations.csv. In particular, some network/arm datasets are exercised as single-arm logits, multi-arm continuous data use arms 1–2, and participant-level recurrence data are summarized into arm means/SDs/n and tested as MD. These tests establish arithmetic agreement for the supplied independent-effect model; they do not endorse ignoring dependence, combining different treatments, or replacing the published analyses. Source-row positions refer to each documented prepared configuration, not universal study identifiers. No PMIDs, NCT IDs, dates, or research effect estimates were invented.

| Dataset | Status | Configurations (k) / exclusion reason |
|---|---|---|
| dat.aloe2013 | used | PCOR (5); ZPCOR (5); SPCOR (5) |
| dat.anand1999 | used | RR (34) |
| dat.anker2025 | used | IRR (6); GEN (6) |
| dat.assink2016 | used | SMD (100) |
| dat.axfors2021 | used | OR (33) |
| dat.bakdash2021 | used | ZCOR stored (678) |
| dat.baker2009 | used | PLO arm-level (94) |
| dat.bangertdrowns2004 | used | SMD (48) |
| dat.bartos2023 | used | PR (96) |
| dat.baskerville2012 | used | SMD stored (23) |
| dat.bassler2004 | used | RR (10) |
| dat.bauer2002 | used | CLES (5); PLO (5) |
| dat.bcg | used | RR (13) |
| dat.begg1989 | used | PR (20) |
| dat.berkey1998 | used | MD (10) |
| dat.berkey1998r | used | stored yi/vi (10) |
| dat.besson2016 | used | SMD (389) |
| dat.bonett2010 | used | ARAW (9); AHW (9); ABT (9) |
| dat.bornmann2007 | used | OR (66) |
| dat.bourassa1996 | used | OR (96) |
| dat.cannon2006 | used | OR endpoint1 (4); OR endpoint2 (4); OR endpoint3 (4); OR endpoint4 (4); OR endpoint5 (4); OR endpoint6 (4) |
| dat.chiarito2020 | used | OR (8) |
| dat.cohen1981 | used | ZCOR (20) |
| dat.colditz1994 | used | RR (13) |
| dat.collins1985a | used | OR recurrent bleeding (25) |
| dat.collins1985b | used | OR (9) |
| dat.craft2003 | used | COR (54) |
| dat.crede2010 | used | ZCOR (97) |
| dat.crisafulli2020 | used | PLN (26) |
| dat.curtin2002 | used | MD stored (21) |
| dat.curtis1998 | used | ROM (102) |
| dat.dagostino1998 | used | SMD (34); OR (68) |
| dat.damico2009 | used | OR (16) |
| dat.debruin2009 | used | PR (13) |
| dat.demir2022 | used | ABT (33) |
| dat.dogliotti2014 | used | PLO arm-level (44) |
| dat.dong2013 | used | PLO arm-level (99) |
| dat.dorn2007 | used | RR (19) |
| dat.dumouchel1994 | used | OR (9) |
| dat.egger2001 | used | RR (16) |
| dat.feng2019 | used | PLO (19) |
| dat.fine1993 | used | stored yi/vi (66) |
| dat.franchini2012 | used | MD arms 1-2 (7) |
| dat.frank2008 | used | OR (4); REH (4) |
| dat.furukawa2003 | used | SMD (17) |
| dat.gibson2002 | used | SMD (13); RR (7); PBIT (15) |
| dat.graves2010 | used | RR (17) |
| dat.greb2008 | used | RR (14) |
| dat.greenland1992 | used | coefficient stored (16) |
| dat.gurusamy2011 | used | PLO arm-level (29) |
| dat.hackshaw1998 | used | OR (37); GEN (37) |
| dat.hahn2001 | used | RR (12) |
| dat.hannum2020 | used | PR (35) |
| dat.hart1999 | used | IRR (6); IRD (6) |
| dat.hartmannboyce2018 | used | RR (136) |
| dat.hasselblad1998 | used | PLO (50); OR (26) |
| dat.higgins2008 | used | RR available case (17) |
| dat.hine1989 | used | RD (6) |
| dat.huber2000 | used | MD recurrence IPD (5) |
| dat.ishak2007 | used | MD (82); stored yi/vi (82) |
| dat.kalaian1996 | used | stored yi/vi (67) |
| dat.karner2014 | used | OR (22); MD (9) |
| dat.kearon1998 | used | OR (30); PLO (28) |
| dat.knapp2017 | used | stored yi/vi (66) |
| dat.konstantopoulos2011 | used | SMD (56) |
| dat.landenberger2005 | used | OR (58) |
| dat.laopaiboon2015 | used | RR (15) |
| dat.lau1992 | used | RR (33) |
| dat.lee2004 | used | RR (16) |
| dat.lehmann2018 | used | stored yi/vi (81) |
| dat.li2007 | used | OR (22) |
| dat.lim2014 | used | ZCOR (170) |
| dat.linde2005 | used | RR (23) |
| dat.linde2015 | used | RR response arms 1-2 (59) |
| dat.linde2016 | used | PLO arm-level (201) |
| dat.lloyd2010 | used | MD das (13); MD haq (8) |
| dat.lopez2019 | used | stored yi/vi (96) |
| dat.maire2019 | used | Mann-Kendall s1 stored (35) |
| dat.mccurdy2020 | used | GEN (1653) |
| dat.mcdaniel1994 | used | ZCOR (160); COR (160) |
| dat.meeker2017 | used | GEN (10) |
| dat.metap | excluded | P-value-only examples; no study effect estimates with sampling variances or documented escalc ingredients |
| dat.michael2013 | used | stored yi/vi (12); MD (12) |
| dat.molloy2014 | used | ZCOR (16) |
| dat.moore1998 | used | RR (37) |
| dat.moura2021 | used | ZCOR (1828) |
| dat.nakagawa2007 | used | ZCOR (15) |
| dat.nielweise2007 | used | OR (17) |
| dat.nielweise2008 | used | IRR (9) |
| dat.nissen2007 | used | OR (38) |
| dat.normand1999 | used | MD (9); SMD (9); ROM (9) |
| dat.obrien2003 | used | RR (30); PR (43) |
| dat.pagliaro1992 | used | PLO (54) |
| dat.pignon2000 | used | stored yi/vi (65) |
| dat.poole2003 | used | MD (17) |
| dat.pritz1997 | used | PR (14); PLO (14) |
| dat.quan2000 | used | RR (11) |
| dat.raudenbush1985 | used | SMD (19) |
| dat.riley2003 | used | GEN (98) |
| dat.rivera2025 | used | log diagnostic OR (10) |
| dat.roever2022 | used | PLO arm-level (37) |
| dat.senn2013 | used | MN (53); MD (27) |
| dat.spooner2002 | used | MD (17) |
| dat.steurer2006 | used | logHR stored (4) |
| dat.stowe2010 | used | MD arms 1-2 (29) |
| dat.tannersmith2016 | used | stored yi/vi (113) |
| dat.thompson1999 | used | logOR stored (28) |
| dat.tian2009 | used | PLO arm-level (96) |
| dat.ursino2021 | used | PLO arm-level (49) |
| dat.vanhowe1999 | used | OR (33) |
| dat.viechtbauer2021 | used | OR (20) |
| dat.white2020 | used | ZCOR (186) |
| dat.woods2010 | used | PLO arm-level (8) |
| dat.yusuf1985 | used | RR (118) |

## Reference execution and reproducibility

reference.R calls actual metafor::rma(method="REML",test="z"), leave1out(), influence(), and baujat(), plus DL and FE controls. All requested R quantities are saved at 17 significant digits. Threshold=1e−12 × max(1, starting tau-squared) and maxiter=10000 tighten convergence without requesting sub-ULP accuracy for large variance scales; an independent scalar score supplies only starting values through the supported control/code2 interfaces. No tau2= override freezes the variance, and all deletion fits still go through metafor’s Fisher scoring and likelihood checks. Early standard-R checkpoints used stepadj=.5 without the initializer; final accelerated results use stepadj=1. Those earlier outputs are retained as an independent numerical cross-check.

The installed reference BLAS was prohibitively slow for repeated dense matrix products. prepare_fast_r.py copies the existing R runtime into this folder and gives the already-installed SciPy OpenBLAS DLL the export names expected by R. Only PE symbol names/order are changed; numerical machine code and metafor code are unchanged. No downloads, package installation, or system edits occurred. The exact DLL hashes and aliases are in blas-provenance.json. OPENBLAS_NUM_THREADS=2 bounds threads. The local runtime passed matrix and metafor smoke tests.

Standard-R versus accelerated-R cross-check: 19879/19879 numeric checks across 29 configurations; largest normalized difference 1.177090768607161e-10, tolerance 1e−9. See blas-verification.json. All boolean/string/null outputs are also checked for equality.

Repeated deletion fits are reused across the actual leave1out/influence/baujat calls through cache_refits.R. Every distinct fit is computed by the original metafor rma.uni function; the wrapper normalizes only the equivalent intercept-only design, selects a union of requested output fields, verifies the full effect/variance vectors, and keys on omitted row, method, test, level, and exact serialized controls. No browser outputs enter this reference. Cache and file-worker cross-check: 32928/32928 numeric checks across 78 configurations; maximum normalized difference 0. The two largest configurations use three local R subprocesses (one BLAS thread each) with RDS checkpoints every 60 deletions. Workers communicate through files, not external services. See reference_parallel.R, prime_refits_files.R, refit_worker.R, and cache-verification.json.

radial_reference.R separately calls metafor::radial() on FE fits for all configurations; its returned coordinates replace the initial formula-based radial references in the final merged artifact. data(package="metafor") contains no additional datasets (metafor-dataset-inventory.json). Startup/performance experiments and interrupted logs are retained for audit; commands.ps1 is the final reproducible workflow.

Reference configurations with captured warnings: 0. See reference-warnings.json for exact text and reference.json for errors or null deletion quantities. R startup locale warnings are retained in run logs. PowerShell returned nonzero wrapper statuses despite completed R runs. The native-exit checks below confirmed successful checkpoint validation and completion directly, bypassing PowerShell stderr/status translation. A reference refusal is not counted as a match unless the browser also refuses; missing results are never imputed.

The final reproducible commands are in commands.ps1 (run from this folder):

```powershell
# Run from this job directory. R_LIBS_USER is the supplied preinstalled package library.
$env:R_LIBS_USER = (Resolve-Path '..\re\Rlib_dta').Path
$env:OPENBLAS_NUM_THREADS = '2'
python setup.py
Rscript inspect.R
Rscript build_corpus.R
Rscript reference_baseline.R
node runner.cjs original app.json
python make_patch.py
node runner.cjs patched app-patched.json
# Optional speedup uses only the already installed R and SciPy binaries.
python prepare_fast_r.py
.\portable-r\bin\Rscript.exe blas_smoke.R
.\portable-r\bin\Rscript.exe reference_accelerated.R --small
.\portable-r\bin\Rscript.exe reference_cached.R --verify2
.\portable-r\bin\Rscript.exe reference_cached.R --medium
$env:OPENBLAS_NUM_THREADS = '1'
.\portable-r\bin\Rscript.exe reference_parallel.R --verify
.\portable-r\bin\Rscript.exe reference_parallel.R
.\portable-r\bin\Rscript.exe radial_reference.R
python merge_reference.py
python compare.py app.json original
python compare.py app-patched.json patched
python verify_blas.py
python verify_cache.py
python report.py
python verify_artifacts.py
```

The last dataset's REML fits were also started with `.\portable-r\bin\Rscript.exe precompute_last.R` while the preceding dataset's diagnostics ran. A Windows file lock in prime_compute.py coordinates this optional overlap; the main run validates and reuses the same checkpoints. The corresponding DL control was overlapped with `precompute_last_dl.R`, using one worker. The sequential commands above produce the same reference. Historical interrupted run logs are retained.

commands.ps1 is the rerun entry point. Checkpoints are reused, so remove the local reference-parts directories (or use a fresh job directory) before a fully fresh run. No source files, project registry, workbook, remote repository, or deployment were changed. This is a validation report and proposed fix, not a release certification.

## Static versus dynamic disclosure

| Item | Kind | Evidence |
|---|---|---|
| Formula constants and flag thresholds | Static | Shipped JavaScript and installed metafor source dumps |
| Column mappings / selected definitions | Static recipes | Installed package docs, build_corpus.R, supplements.R |
| Effects and variances | Dynamic | Real metadat extraction and escalc; corpus.json |
| Reference and app outputs | Dynamic | Actual R and Chrome runs |
| Counts, pass totals, maxima | Dynamic | compare.py, report.py, results.json |
| Runtime/source locations | Static harness configuration | Supplied task environment; no pushed product code |

## Final console lines

```text
python merge_reference.py
REFERENCE 142/142 configurations; 0 pending
python compare.py app.json original
155797/183990 checks pass
python compare.py app-patched.json patched
164802/164802 checks pass
python verify_blas.py
BLAS CROSS-CHECK 19879/19879 numeric checks pass across 29 configurations; max difference 1.177090768607161e-10
python verify_cache.py
CACHE CROSS-CHECK 32928/32928 numeric checks pass across 78 configurations; max difference 0
```

Native exit confirmations (verbatim console output):

```text
R NATIVE EXIT 0: precompute_last.R; log precompute-last-verified.log
R NATIVE EXIT 0: precompute_last_dl.R; log precompute-last-dl-verified.log
R NATIVE EXIT 0: reference_parallel.R; log reference-parallel-verified.log
```
