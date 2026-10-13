# Run from this job directory. R_LIBS_USER is the supplied preinstalled package library.
$env:R_LIBS_USER = '<R_LIBS_USER>'
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
