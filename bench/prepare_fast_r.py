from pathlib import Path
import shutil,struct,json,hashlib
import scipy
from inspect_blas import exports
root=Path('<R_HOME>');dest=Path('portable-r')
shutil.copytree(root,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('doc','tests','demo'))
source=next((Path(scipy.__file__).parent.parent/'scipy.libs').glob('*.dll'))
b,names,an,ao=exports(source)
original=dest/'bin/x64/Rblas.dll'
_,required,_,_=exports(original);required={x[0] for x in required}
renamed=[]
for name,no,nr,ordinal in names:
 new=name.removeprefix('scipy_')
 if new in required:
  b[no:no+len(name)+1]=new.encode()+b'\0'*(len(name)+1-len(new))
  renamed.append([name,new]); name=new
 names2=locals().setdefault('names2',[]);names2.append((name,nr,ordinal))
for i,(name,nr,ordinal) in enumerate(sorted(names2)):
 struct.pack_into('<I',b,an+4*i,nr);struct.pack_into('<H',b,ao+2*i,ordinal)
original.write_bytes(b)
Path('blas-provenance.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'local_sha256':hashlib.sha256(b).hexdigest(),'change':'PE exported-symbol aliases only; OpenBLAS numerical machine code unchanged','aliases':renamed},indent=2))
print('Prepared local R with installed SciPy OpenBLAS; no system files modified')
