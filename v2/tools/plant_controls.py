"""Three real validate.R corruption runs, restoring exact bytes even on failure.
Usage: python v2/tools/plant_controls.py <Rscript executable>
Run only when the main validation is idle. No pin inventory is changed.
"""
import json,os,re,subprocess,sys
from pathlib import Path
from validate import ROOT,V2,OUT,sha

def app(raw):
    obj=json.loads(raw);cid=sorted(obj)[0];obj[cid]['full']['Qp']+=1e-3
    return json.dumps(obj).encode()

def fit(raw):
    lines=raw.decode().splitlines();obj=json.loads(lines[1]);obj['mu']+=1e-3;lines[1]=json.dumps(obj)
    return ('\n'.join(lines)+'\n').encode()

def script(raw):
    text=raw.decode()
    text,n=re.subn(r'("full[.]mu" = list\(app = )([-+0-9.eE]+)',lambda m:m[1]+str(float(m[2])+1e-3),text,count=1)
    if n!=1: raise ValueError('Cannot locate E3 expected full.mu')
    return text.encode()

def main(rscript):
    out=OUT/'plants';out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['INFLUENCE_V2_ONLY']='1';env['R_ENVIRON_USER']='NUL';env['LC_ALL']='C'
    controls=[('capture',V2/'captures/cap_f96772b.json',app),
              ('stored_fit',V2/'e1/refits.jsonl',fit),('e3_expected',V2/'e3_scripts/s00.R',script)]
    results=[]
    for name,path,mutate in controls:
        raw=path.read_bytes();before=sha(path)
        try:
            bad=mutate(raw);assert bad!=raw;path.write_bytes(bad)
            log=out/(name+'.log')
            with log.open('w',encoding='utf-8') as f:
                run=subprocess.run([rscript,'validate.R'],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
            text=log.read_text()
            assert run.returncode!=0 and 'V2 NOT REPRODUCED' in text and 'SHA-256 mismatch' in text,text
            results.append(dict(control=name,exit=run.returncode,verdict='V2 NOT REPRODUCED'))
            print(f'PLANTED {name} 1/1 rejected; exit {run.returncode}')
        finally:
            path.write_bytes(raw)
            assert sha(path)==before
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PLANTED INPUTS 3/3 rejected; RESTORED 3/3 byte-identical')

if __name__=='__main__':main(sys.argv[1])
