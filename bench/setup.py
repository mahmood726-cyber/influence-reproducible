from pathlib import Path
import shutil, re, hashlib, json, subprocess
root=Path('<ALLMETA_WORKTREE>')
dest=Path('original')
queue=[Path('influence/index.html')]
seen=set()
while queue:
    rel=queue.pop()
    if rel in seen: continue
    seen.add(rel)
    src=root/rel
    if not src.is_file(): continue
    out=dest/rel; out.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,out)
    if src.suffix=='.html':
        for ref in re.findall(r'(?:src|href)="([^"]+)"',src.read_text(encoding='utf-8')):
            if not ref.startswith(('http:','https:','#','data:')):
                resolved=(src.parent/ref).resolve()
                if resolved.is_file(): queue.append(resolved.relative_to(root.resolve()))
manifest={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}
Path('source-manifest.json').write_text(json.dumps({'commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'sha256':manifest},indent=2))
