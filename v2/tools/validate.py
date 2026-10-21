"""Run the v2 archive contract from validate.R; Python standard library only."""
from pathlib import Path
import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / 'v2'
OUT = ROOT / 'outputs/v2'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def pairs(items):
    result = {}
    for k, v in items:
        require(k not in result, 'Duplicate JSON key: ' + k)
        result[k] = v
    return result

def loads(text):
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON: '+x)))

def read(path):
    return loads(Path(path).read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inventory():
    # This exact coverage rule prevents an empty/partial pin file from passing.
    files = {p.relative_to(ROOT).as_posix() for p in V2.rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and p.name != 'INPUT_SHA256.json'}
    files |= {'data/corpus.json', 'results/reference.json', 'results/app-patched.json'}
    pins = read(V2/'INPUT_SHA256.json')
    require(set(pins) == files, 'V2 input inventory coverage mismatch')
    passed = sum((ROOT/p).is_file() and sha(ROOT/p) == h for p, h in pins.items())
    print(f'V2 INPUT SHA256 {passed}/{len(pins)}', flush=True)
    require(passed == len(pins), 'V2 input SHA-256 mismatch: '+', '.join(p for p,h in pins.items() if sha(ROOT/p) != h))
    app = V2/'app'
    ap = read(app/'app-sha256.json')
    actual = {p.relative_to(app).as_posix(): sha(p) for p in app.rglob('*')
              if p.is_file() and p.name != 'app-sha256.json'}
    require(ap == actual, 'V2 app SHA-256 inventory mismatch')
    print(f'V2 APP SHA256 {len(ap)}/{len(ap)}', flush=True)
    # The historical preregistration list includes its original, unedited generator.
    for line in (V2/'PREREG_SHA256.txt').read_text().splitlines():
        m = re.fullmatch(r'([0-9a-f]{64}) \*(.+)', line)
        if m:
            require(sha(V2/m[2]) == m[1], 'Preregistration SHA-256 mismatch: '+m[2])
    print('V2 PREREG SHA256 3/3', flush=True)

def bit_identity(capture, expected):
    old = read(ROOT/'results/app-patched.json')
    require(set(capture) == set(old), 'Bit identity configuration coverage')
    count = passed = 0
    def compare(a,b):
        nonlocal count,passed
        if isinstance(a,dict):
            require(isinstance(b,dict) and set(a) <= set(b),'Bit identity keys')
            for k in a: compare(a[k],b[k])
        elif isinstance(a,list):
            require(isinstance(b,list) and len(a)==len(b),'Bit identity cardinality')
            for x,y in zip(a,b): compare(x,y)
        else:
            require(type(a) in (int,float) and type(b) in (int,float),'Bit identity numeric type')
            count += 1
            passed += struct.pack('>d',a) == struct.pack('>d',b)
    fields = {'full': ['mu','seMu','tau2','Q','df','wRE','swRE'],
              'baujat':['x','y','mu','tau2'], 'radial':['x','z','slope','resid']}
    for cid,a in old.items():
        b=capture[cid]
        for group, keys in fields.items():
            compare({k:a[group][k] for k in keys},b[group])
        keys=['hat','resid','dffits','cooksD','covRatio','loo_mu','loo_seMu']
        compare([{k:d[k] for k in keys} for d in a['diag']],b['diag'])
    print(f'V2 BIT IDENTITY {passed}/{count}',flush=True)
    require(count == passed == expected,'Bit identity mismatch')

def refits(path, sets):
    lines=[loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]
    require(lines[-1] == {'done':True},'Incomplete refit run')
    env=lines[0]['env']
    require(env['metafor']=='5.2.1' and env['jsonlite']=='2.0.0' and '4.6.0' in env['R'],'Refit versions')
    wanted={('F',cid):s['exclude'] for cid,s in sets['F'].items() if not s['refused']}
    wanted.update({('R'+str(s['rep']),s['id']):s['exclude'] for s in sets['R']})
    fits={}
    for r in lines[1:-1]:
        key=(r['tag'],r['id'])
        require(key not in fits and key in wanted and 'error' not in r,'Unexpected/duplicate/error refit '+str(key))
        excl=r['exclude'] if isinstance(r['exclude'],list) else [r['exclude']]
        require(excl == wanted[key],'Refit exclusion mismatch '+str(key))
        fits[key]=r
    require(set(fits)==set(wanted) and len(fits)==494,'Refit coverage mismatch')
    return fits

def compare_refits(stored, fresh, sets, tolerance):
    a,b=refits(stored,sets),refits(fresh,sets)
    fields=['mu','se','zval','pval','ci.lb','ci.ub','tau2','I2','H2','QE','QEp']
    passed=0; maximum=0
    for key in a:
        require(a[key]['k']==b[key]['k'],'Refit k mismatch '+str(key))
        ok=True
        for q in fields:
            x,y=a[key][q],b[key][q]
            require(type(x) in (int,float) and type(y) in (int,float) and math.isfinite(x) and math.isfinite(y),'Refit numeric type')
            error=abs(x-y)/max(1,abs(y));maximum=max(maximum,error)
            ok &= error<=tolerance
            if error>tolerance: print(f'REFIT FAIL {key} {q}: stored={x} fresh={y} diff={error}',flush=True)
        passed+=ok
    print(f'V2 FRESH REFITS {passed}/{len(a)} | max normalized diff {maximum:.17g} | tolerance {tolerance:g}',flush=True)
    require(passed==494,'Stored/fresh refit mismatch')

def run(command, cwd, log):
    with Path(log).open('w',encoding='utf-8') as f:
        result=subprocess.run([str(x) for x in command],cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
    return result.returncode,Path(log).read_text(encoding='utf-8',errors='replace')

def comparator(name, arguments, lines):
    code,text=run([sys.executable,V2/'tools'/name,*arguments],OUT,OUT/(name+'.log'))
    print(text,flush=True)
    require(code==0,name+' exited '+str(code))
    for line in lines: require(line in text,name+' missing exact denominator: '+line)

def main(rscript):
    start=time.monotonic()
    OUT.mkdir(parents=True,exist_ok=True)
    inventory()
    ex=read(V2/'expected/paper_values.json')
    sets=read(V2/'e1/sets.json')
    require(len(sets['F'])==ex['flagged_configurations'] and sum(s['refused'] for s in sets['F'].values())==ex['refused'],'F set contract')
    require(len(sets['R'])==ex['R_fits'] and len({s['id'] for s in sets['R']})==ex['random_configurations'],'R set contract')
    corpus=read(ROOT/'data/corpus.json'); capture=read(V2/'captures/cap_f96772b.json')
    exclusion=read(V2/'captures/e1app_f96772b.json')
    require(len(corpus)==ex['configurations'] and sum(len(c['yi']) for c in corpus.values())==ex['effect_rows'],'Corpus contract')
    require(set(corpus)==set(capture)==set(exclusion),'Capture coverage mismatch')
    bit_identity(capture,ex['bit_identity'])
    comparator('e2_compare.py',[V2/'captures/cap_f96772b.json','fresh'],[f"E2 TOTAL {ex['E2']}/{ex['E2']} checks pass"])
    print(f"V2 E2 {ex['E2']}/{ex['E2']}",flush=True)
    print('V2 E1: starting 494 fresh metafor 5.2.1 fits',flush=True)
    fresh=OUT/'fresh_refits.jsonl'
    # refit.R truncates this file; no historical checkpoint is read.
    code,text=run([rscript,'--vanilla',V2/'e1/refit.R',ROOT/'data/corpus.json',V2/'e1/sets.json',fresh],ROOT,OUT/'refit.log')
    print(text,flush=True)
    require(code==0,'Fresh R refit execution failed')
    compare_refits(V2/'e1/refits.jsonl',fresh,sets,ex['stored_refit_tolerance'])
    comparator('e1_compare.py',[V2/'captures/e1app_f96772b.json',fresh,V2/'e1/sets.json','fresh'],
               [f"SET {s}: {ex[key]}/{ex[key]} checks pass" for s,key in [('S','S'),('F','F'),('R','R_checks')]]+
               [f"E1 TOTAL {ex['E1']}/{ex['E1']} checks pass"])
    for s,key in [('S','S'),('F','F'),('R','R_checks'),('TOTAL','E1')]: print(f'V2 E1 {s} {ex[key]}/{ex[key]}',flush=True)
    manifest=read(V2/'e3_scripts/manifest.json')
    scripts=manifest['scripts']
    require(not manifest['pageerrors'] and len(scripts)==34 and len({s['file'] for s in scripts})==34,'E3 manifest coverage')
    require([s['id'] for s in scripts if not s['planted']]==sets['E3'],'E3 sample mismatch')
    require({s['file'] for s in scripts if s['planted']}=={'s00_planted.R','s10_planted.R','s20_planted.R'},'E3 planted coverage')
    require({s['file'] for s in scripts if not s['planted']}==set(ex['E3_per_script']),'E3 value-count coverage')
    results=[];passed=planted=values=0
    for s in scripts:
        path=V2/'e3_scripts'/s['file']
        require(sha(path)==s['sha256'],'E3 original script SHA-256 mismatch: '+s['file'])
        work=OUT/'e3'/path.stem;work.mkdir(parents=True,exist_ok=True)
        print('V2 E3 START '+s['file'],flush=True)
        t0=time.monotonic()
        code,text=run([rscript,'--vanilla',path],work,work/'run.log')
        matches=re.findall(r'^ALL (\d+)/(\d+) app values reproduced\s*$',text,re.M)
        require('metafor 5.2.1, R version 4.6.0' in text,'E3 runtime mismatch')
        if s['planted']:
            require(code==1 and re.search(r'^FAIL 1/\d+ app values differ beyond tolerance',text,re.M) and not matches,'Planted E3 must fail exactly one value: '+s['file'])
            planted+=1
            verdict='expected FAIL, exit 1'
        else:
            require(code==0 and len(matches)==1,'E3 script did not reproduce: '+s['file'])
            n,m=map(int,matches[0]);require(n==m==ex['E3_per_script'][s['file']],'E3 per-script denominator')
            values+=n;passed+=1;verdict=f'ALL {n}/{n} app values reproduced'
        results.append(dict(file=s['file'],exit=code,seconds=time.monotonic()-t0,verdict=verdict))
        print('V2 E3 '+s['file']+' '+verdict,flush=True)
        (OUT/'e3_results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(f"V2 E3 SCRIPTS {passed}/{ex['E3_scripts']}",flush=True)
    print(f"V2 E3 VALUES {values}/{ex['E3_values']}",flush=True)
    print(f"V2 E3 PLANTED {planted}/{ex['E3_planted']} expected failures",flush=True)
    require((passed,values,planted)==(ex['E3_scripts'],ex['E3_values'],ex['E3_planted']),'E3 totals')
    print(f'V2 elapsed seconds {time.monotonic()-start:.1f}',flush=True)

if __name__=='__main__':
    try:
        main(sys.argv[1])
    except Exception as error:
        print('V2 validation failed: '+str(error),flush=True)
        sys.exit(1)
