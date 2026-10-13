from pathlib import Path
import json,math,struct,hashlib
old={};new={}
for folder in ['reference-parts','reference-fast-parts','reference-baseline-parts']:
 for p in Path(folder).glob('*.json'):old.update(json.loads(p.read_text()))
for p in Path('reference-accelerated-parts').glob('*.json'):new.update(json.loads(p.read_text()))
checks=0;maximum=0;worst=None
def compare(a,b,path):
 global checks,maximum,worst
 if isinstance(a,dict):
  for k in a:
   if k not in ['warnings']:compare(a[k],b[k],path+'.'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),path
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,f'{path}[{i}]')
 elif isinstance(a,(int,float)) and not isinstance(a,bool):
  checks+=1;assert isinstance(b,(int,float)),path
  err=abs(a-b)/max(1,abs(a))
  if err>maximum:maximum=err;worst=path
  assert err<=1e-9,(path,err)
 else:assert a==b,(path,a,b)
ids=sorted(old.keys()&new.keys())
for id in ids:compare(old[id],new[id],id)
result=dict(configurations=len(ids),numeric_checks=checks,max_normalized_difference=maximum,worst=worst,tolerance=1e-9)
prov=json.loads(Path('blas-provenance.json').read_text())
source=Path(prov['source']).read_bytes();local=Path('portable-r/bin/x64/Rblas.dll').read_bytes()
pe=struct.unpack_from('<I',source,0x3c)[0];coff=pe+4
n=struct.unpack_from('<H',source,coff+2)[0];sz=struct.unpack_from('<H',source,coff+16)[0]
code_sections={}
for i in range(n):
 pos=coff+20+sz+i*40;flags=struct.unpack_from('<I',source,pos+36)[0]
 if flags & 0x20000020:
  name=source[pos:pos+8].split(b'\0')[0].decode();size,off=struct.unpack_from('<II',source,pos+16)
  assert source[off:off+size]==local[off:off+size],name
  code_sections[name]=hashlib.sha256(source[off:off+size]).hexdigest()
result['unchanged_machine_code_sections']=code_sections
Path('blas-verification.json').write_text(json.dumps(result,indent=2))
print(f'BLAS CROSS-CHECK {checks}/{checks} numeric checks pass across {len(ids)} configurations; max difference {maximum:.17g}')
