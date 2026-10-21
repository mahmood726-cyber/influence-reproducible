"""Build release inventories using v1's source selection rule; does not change v1 pins."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
EXCLUDED={'.git','__pycache__','.pytest_cache','outputs','.validate-work'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
def sources():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(x in EXCLUDED or x.startswith('.verify-') for x in p.relative_to(ROOT).parts)
                  and p.name not in {'SOURCE_SHA256.json','PROGRESS.md'}
                  and p.relative_to(ROOT).as_posix() not in {'validate_full.log','validate_full_run.json'})
if __name__=='__main__':
    files=[p for p in (ROOT/'v2').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='INPUT_SHA256.json']
    files += [ROOT/p for p in ['data/corpus.json','results/reference.json','results/app-patched.json']]
    write(ROOT/'v2/INPUT_SHA256.json',{p.relative_to(ROOT).as_posix():sha(p) for p in files})
    write(ROOT/'SOURCE_SHA256.json',{p.relative_to(ROOT).as_posix():sha(p) for p in sources()})
    print('Refreshed v2 input inventory and release source inventory; original v1 pins untouched.')
