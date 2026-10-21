"""Fast negative controls, using actual captures and fresh outputs; no new fits."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import validate as v

def rejected(fn):
    try:
        fn()
    except (ValueError,AssertionError):
        return
    raise AssertionError('Planted defect was accepted')

def main():
    out=v.OUT/'safeguards';out.mkdir(parents=True,exist_ok=True)
    def feature(path):
        source=path.read_text()
        assert all(s in source for s in ['INFLUENCE_V2_ONLY','v2_main()','V2 NOT REPRODUCED','V2 REPRODUCED'])
    rejected(lambda:feature(v.V2/'provenance/v1-release/validate.R'))
    print('V2 ENTRYPOINT original 0/1 (expected failure)')
    feature(v.ROOT/'validate.R')
    print('V2 ENTRYPOINT current 1/1')
    capture=v.read(v.V2/'captures/cap_f96772b.json')
    v.bit_identity(capture,126000)
    capture[sorted(capture)[0]]['full']['mu']+=1e-3
    rejected(lambda:v.bit_identity(capture,126000))
    print('BIT IDENTITY CORRUPTION 1/1 rejected')
    sets=v.read(v.V2/'e1/sets.json')
    fresh=v.OUT/'fresh_refits.jsonl'
    v.compare_refits(v.V2/'e1/refits.jsonl',fresh,sets,1e-12)
    lines=(v.V2/'e1/refits.jsonl').read_text().splitlines()
    row=json.loads(lines[1]);row['mu']+=1e-3;lines[1]=json.dumps(row)
    with contextlib.nullcontext(out/'fixtures') as temp:
        temp.mkdir(parents=True,exist_ok=True)
        bad=Path(temp)/'refits.jsonl';bad.write_text('\n'.join(lines)+'\n')
        rejected(lambda:v.compare_refits(bad,fresh,sets,1e-12))
        print('REFIT NUMERIC CORRUPTION 1/1 rejected')
        bad.write_text('\n'.join(lines[:-1])+'\n')
        rejected(lambda:v.refits(bad,sets))
        print('INCOMPLETE REFITS 1/1 rejected')
        root=Path(temp)/'archive';layer=root/'v2';layer.mkdir(parents=True,exist_ok=True)
        (layer/'INPUT_SHA256.json').write_text('{}')
        original_root,original_v2=v.ROOT,v.V2
        try:
            v.ROOT,v.V2=root,layer
            rejected(v.inventory)
        finally:
            v.ROOT,v.V2=original_root,original_v2
        print('EMPTY HASH INVENTORY 1/1 rejected')
    for name,args,marker in [
        ('e2_compare.py',[v.V2/'captures/cap_f96772b.json','planted','--plant'],'E2 TOTAL 96646/96650'),
        ('e1_compare.py',[v.V2/'captures/e1app_f96772b.json',fresh,v.V2/'e1/sets.json','planted','--plant'],'failures 4')]:
        code,text=v.run([sys.executable,v.V2/'tools'/name,*args],out,out/(name+'.log'))
        print(text)
        assert code==1 and marker in text
        print(name+' PLANTED 1/1 rejected')
    print('SAFEGUARDS 8/8 passed')

if __name__=='__main__':main()
