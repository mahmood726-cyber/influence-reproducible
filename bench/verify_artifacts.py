from pathlib import Path
import json,hashlib,math,subprocess
load=lambda p:json.loads(Path(p).read_text())
corpus=load('corpus.json');audit=load('corpus-audit.json');ref=load('reference.json')
assert len(audit)==114
assert set(corpus)==set(ref),'Reference coverage incomplete'
assert all(v.get('error') is None for v in ref.values()),'Reference refusal exists; review report'
for id,c in corpus.items():
 assert id==c['dataset']+'::'+c['definition']
 assert len(c['yi'])==len(c['vi'])==len(c['rows']) and len(c['yi'])>=3
 assert all(math.isfinite(y) for y in c['yi']) and all(math.isfinite(v) and v>0 for v in c['vi'])
for name in ['app.json','app-patched.json']:
 a=load(name);assert set(a)==set(corpus)
 assert not load(name+'.errors.json')
 for id,v in a.items():
  assert 'error' not in v
  assert len(v['diag'])==len(corpus[id]['yi'])
  for i,d in enumerate(v['diag']):
   assert d['te']==corpus[id]['yi'][i]
   assert math.isclose(d['se']**2,corpus[id]['vi'][i],rel_tol=1e-14,abs_tol=0)
   assert d['label']==f"row{corpus[id]['rows'][i]}"
  assert v['ui']['tableRows']==len(v['diag'])+1
  assert all(n>0 for n in v['ui']['plots'])
manifest=load('source-manifest.json')
for rel,sha in manifest['sha256'].items():
 for base in [Path('original'),Path('<ALLMETA_WORKTREE>')]:
  assert hashlib.sha256((base/rel).read_bytes()).hexdigest()==sha,(base,rel)
subprocess.run(['git','-C','original','apply','--check','../fix.patch'],check=True)
assert load('results-patched.json')['passes']==load('results-patched.json')['checks'],'Patched numerical checks fail'
assert load('blas-verification.json')['numeric_checks']>0
assert load('cache-verification.json')['numeric_checks']>0
assert set(load('radial-reference.json'))==set(corpus)
files=['corpus.json','corpus-audit.json','reference.json','app.json','app-patched.json','fix.patch','results.json','RESULTS.md']
files+=sorted(str(p) for pattern in ['*.R','*.py','*.cjs','*.ps1'] for p in Path('.').glob(pattern))
Path('artifact-sha256.json').write_text(json.dumps({p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},indent=2))
print(f'ARTIFACT CHECK PASS: {len(corpus)} configurations; complete R/browser coverage; source unchanged; patch applies')
