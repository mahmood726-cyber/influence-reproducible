from pathlib import Path
import json
corpus=json.loads(Path('corpus.json').read_text())
out={}
for folder in ['reference-fast-parts','reference-large-parts','reference-parts','reference-cached-parts','reference-parallel-parts','reference-accelerated-parts']:
 for p in Path(folder).glob('*.json'):
  out.update(json.loads(p.read_text()))
out={k:out[k] for k in corpus if k in out}
if Path('radial-reference.json').exists():
 radial=json.loads(Path('radial-reference.json').read_text())
 for k in out:out[k]['radial']=radial[k]
Path('reference.json').write_text(json.dumps(out,separators=(',',':')))
missing=[k for k in corpus if k not in out]
Path('reference-missing.json').write_text(json.dumps(missing,indent=2))
print(f'REFERENCE {len(out)}/{len(corpus)} configurations; {len(missing)} pending')
