# Changelog

## 1.1.0 (unpublished)

- Add the separate v2 app snapshot and preregistered E1/E2/E3 evidence.
- Extend the one-command validator with fresh exclusion fits, unmodified downloaded R scripts, exact tier counts, version gates and failure controls.
- Pin the v2 app snapshot to the allmeta release identifiers: v1.8.0 (tag commit 1cb3f8409c7af75ed41f7e1811f9c502f900fc79, DOI 10.5281/zenodo.23515177), which contains PR #170. All 437 snapshot files are now byte-for-byte the v1.8.0 Git blobs: 379 already matched, 38 differed only in line endings and 20 in content.
- Add RELEASE_EQUIVALENCE.md: which tier was validated at which allmeta commit, every influence/shared/hub-shared file that differs between c6b8912 and 1cb3f84 classified ENGINE or NON-ENGINE, the 437-file snapshot table, and the execution check. Re-running the page capture, the exclusion-UI harness and the R-script generator on the v1.8.0 bytes reproduced `v2/captures/cap_f96772b.json` and `v2/captures/e1app_f96772b.json` byte for byte and every E3 script body from line 3 onward, with all v2 counts unchanged: bit identity 126000/126000, E2 96650/96650, E1 121913/121913 on 494/494 fresh fits, E3 31/31 scripts and 27637/27637 values, 3/3 planted failures.
- Record the re-pin and the classification in `v2/provenance/repin-v1.8.0.json` and `v2/provenance/engine-scope-c6b8912.json`.
- The v1 primary tier's 164802 checks stay scoped to allmeta c6b8912 (page bytes fd45b9f, allmeta v1.3.0) and are not claimed for v1.8.0; the long default `Rscript validate.R` was not run for this entry.
- `v2/tools/verify_release.py` now also requires the filled allmeta v1.8.0 tag and DOI, no unfilled release token, and the RELEASE_EQUIVALENCE.md record.
- Preserve v1 statistical inputs and counts; cap local validation at two R processes.
- DOI: [ARCHIVE v1.1.0 DOI PENDING]. No upload, tag or publication.

## 1.0.0

- Archive the full primary influence-diagnostics comparison and the before-fix DL controls.
- Record the DFFITS, influential-flag and REML Baujat corrections from allmeta PR #108.
- Include a hash-checked one-command R refit, strict comparison checks, publication outputs, and the self-contained page validation snapshot.
- Record the merged allmeta commits: c6b8912 (PR #108) and fd45b9f (PR #109), both in v1.3.0.
