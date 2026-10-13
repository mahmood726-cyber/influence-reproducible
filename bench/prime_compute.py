from pathlib import Path
import subprocess,os,sys,time,msvcrt
folder=Path(sys.argv[1]);workers=int(sys.argv[2]);jobs=[]
# Coordinate optional precomputation with the main reference process.
# Windows releases this lock automatically if its owning process exits.
lock=(folder/'compute.lock').open('a+b')
if lock.seek(0,2)==0:lock.write(b'0');lock.flush()
while True:
 lock.seek(0)
 try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);break
 except OSError:time.sleep(1)
env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='1'
for i in range(workers):
 log=(folder/f'worker-{i}.log').open('wb')
 p=subprocess.Popen([str(Path('portable-r/bin/Rscript.exe').resolve()),'refit_worker.R',str(folder),str(i),str(workers)],stdout=log,stderr=subprocess.STDOUT,env=env)
 jobs.append((p,log))
codes=[]
for p,log in jobs:codes.append(p.wait());log.close()
lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
if any(codes):raise SystemExit(f'Refit worker failed: {codes}; inspect {folder}')
