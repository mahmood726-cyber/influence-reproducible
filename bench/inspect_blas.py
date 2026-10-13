import struct
from pathlib import Path
def exports(path):
 b=bytearray(Path(path).read_bytes()); pe=struct.unpack_from('<I',b,0x3c)[0]; coff=pe+4
 n=struct.unpack_from('<H',b,coff+2)[0]; sz=struct.unpack_from('<H',b,coff+16)[0]; opt=coff+20
 data=opt+(112 if struct.unpack_from('<H',b,opt)[0]==0x20b else 96)
 sections=[]
 for i in range(n):
  p=opt+sz+i*40; vs,va,rs,rp=struct.unpack_from('<IIII',b,p+8);sections.append((va,max(vs,rs),rp))
 def offset(rva):
  for va,size,rp in sections:
   if va<=rva<va+size:return rp+rva-va
  raise ValueError(rva)
 er=struct.unpack_from('<I',b,data)[0]; eo=offset(er)
 nn,an,ao=struct.unpack_from('<IxxxxII',b,eo+24)
 names=[]
 for i in range(nn):
  nr=struct.unpack_from('<I',b,offset(an)+4*i)[0];no=offset(nr);end=b.index(0,no)
  names.append((b[no:end].decode(),no,nr,struct.unpack_from('<H',b,offset(ao)+2*i)[0]))
 return b,names,offset(an),offset(ao)
if __name__=='__main__':
 import scipy
 scipyblas=next((Path(scipy.__file__).parent.parent/'scipy.libs').glob('*.dll'))
 original=Path('<R_HOME>/bin/x64/Rblas.dll')
 try:
  _,names,_,_=exports(original);_,snames,_,_=exports(scipyblas)
  names=[n[0] for n in names];snames={n[0] for n in snames}
  print('R exports',names)
  print('Missing in SciPy',[n for n in names if 'scipy_'+n not in snames and n not in snames])
 except Exception as e:print(type(e).__name__,e);raise
