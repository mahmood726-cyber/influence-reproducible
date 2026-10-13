from pathlib import Path
import json
def read(folder):
 out={}
 for p in Path(folder).glob('*.json'):out.update(json.loads(p.read_text()))
 return out
a=read('reference-accelerated-parts');b=read('reference-cached-parts');b.update(read('reference-cache-check-parts'))
b.update(read('reference-parallel-parts'))
checks=0;maximum=0
def verify(x,y,path):
 global checks,maximum
 if isinstance(x,dict):
  assert set(x)==set(y),path
  for k in x:
   if k!='warnings':verify(x[k],y[k],path+'.'+k)
 elif isinstance(x,list):
  assert len(x)==len(y),path
  for i,(xx,yy) in enumerate(zip(x,y)):verify(xx,yy,f'{path}[{i}]')
 elif isinstance(x,(int,float)) and not isinstance(x,bool):
  checks+=1;assert y is not None,path
  err=abs(x-y)/max(1,abs(x));maximum=max(maximum,err);assert err<=1e-9,(path,err)
 else:assert x==y,(path,x,y)
ids=sorted(a.keys()&b.keys());assert len(ids)>=2
for id in ids:verify(a[id],b[id],id)
out=dict(configurations=len(ids),numeric_checks=checks,max_normalized_difference=maximum,tolerance=1e-9)
Path('cache-verification.json').write_text(json.dumps(out,indent=2))
print(f'CACHE CROSS-CHECK {checks}/{checks} numeric checks pass across {len(ids)} configurations; max difference {maximum:.17g}')
