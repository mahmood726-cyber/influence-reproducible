"""Capture native R exit status without PowerShell stderr/exit translation."""
from pathlib import Path
import os,subprocess,sys
script,log,*args=sys.argv[1:]
env=os.environ.copy()
env['R_LIBS_USER']=str(Path('../re/Rlib_dta').resolve())
env['OPENBLAS_NUM_THREADS']='1'
with Path(log).open('wb') as f:
 result=subprocess.run([str(Path('portable-r/bin/Rscript.exe').resolve()),script,*args],env=env,stdout=f,stderr=subprocess.STDOUT)
print(f'R NATIVE EXIT {result.returncode}: {script}; log {log}')
raise SystemExit(result.returncode)
