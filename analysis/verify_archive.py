"""Fail-closed archive integrity, complete assets, tables, images and regeneration."""
from pathlib import Path
import hashlib,re,tempfile,csv,json
from PIL import Image
from make_outputs import ROOT,build
from checks import read
EXCLUDED={'.git','__pycache__','.pytest_cache','outputs','.validate-work'}
def sources():return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(x in EXCLUDED or x.startswith('.verify-') for x in p.relative_to(ROOT).parts) and p.name not in {'SOURCE_SHA256.json','PROGRESS.md'})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    pins=read(ROOT/'SOURCE_SHA256.json')
    assert {p.relative_to(ROOT).as_posix():sha(p) for p in sources()}==pins,'Source inventory/hash mismatch'
    app=read(ROOT/'app/app-sha256.json')
    assert app=={p.relative_to(ROOT/'app').as_posix():sha(p) for p in (ROOT/'app').rglob('*') if p.is_file() and p.name!='app-sha256.json'},'App inventory/hash mismatch'
    for p in sources():
        if p.suffix.lower() in {'.json','.js','.mjs','.py','.r','.md','.csv','.txt','.html','.cff','.patch','.css'}:
            raw=p.read_bytes();assert not raw.startswith(b'\xef\xbb\xbf'),str(p)
            text=raw.decode('utf-8');assert not re.search(r'\b[A-Za-z]:[\\/](?:Users|Projects|claude-temp|E156|ProjectIndex)[\\/]',text),f'Machine path: {p}'
        assert p.name not in {'paper.md','paper_v2_dictated_text.md'},'Manuscript draft'
    page=ROOT/'app/influence/index.html'
    for rel in re.findall(r'(?:src|href)="([^"]+)"',page.read_text(encoding='utf-8')):
        if not rel.startswith(('http:','https:','#')) and rel.endswith(('.js','.css')):assert (page.parent/rel).is_file(),rel
    for request in read(ROOT/'app/request-assets.json'):
        assert (ROOT/'app'/request).is_file(),request
    manifest=read(ROOT/'app/influence/validate/MANIFEST.json')
    for f in manifest['files']:
        p=ROOT/'app/influence'/f['path'];assert sha(p)==f['sha256'] and b'\r' not in p.read_bytes()
    title='Influence diagnostics for meta-analysis in the browser: a tool validated against the R package metafor'
    z=read(ROOT/'.zenodo.json');cff=(ROOT/'CITATION.cff').read_text(encoding='utf-8')
    assert z['title']==title and 'title: '+json.dumps(title) in cff
    assert z['creators']==[{'name':'Ahmad, Mahmood'}] and 'family-names: Ahmad' in cff and 'given-names: Mahmood' in cff
    assert z['license']=='MIT' and z['version']=='1.0.0' and 'license: MIT' in cff and 'version: 1.0.0' in cff
    assert {(x['identifier'],x['relation']) for x in z['related_identifiers']}=={('https://github.com/mahmood726-cyber/allmeta','isDerivedFrom'),('10.5281/zenodo.23288388','isDerivedFrom')}
    assert 'c6b8912' in cff and 'c6b8912' in (ROOT/'README.md').read_text(encoding='utf-8') and '<ALLMETA_COMMIT>' not in cff
    c=read(ROOT/'data/corpus.json');inv=list(csv.DictReader((ROOT/'data/dataset-inventory.csv').open(encoding='utf-8')))
    assert len(inv)==114 and len({v['dataset'] for v in c.values()})==113
    t=list(csv.DictReader((ROOT/'outputs/table1_by_quantity.csv').open(encoding='utf-8')))
    assert t and t[-1].get('quantity')=='TOTAL','Invalid or empty quantity table'
    for key,want in [('checks_after',164802),('passed_after',164802),('checks_before',183990),('passed_before',155797)]:assert int(t[-1][key])==sum(int(v[key]) for v in t[:-1])==want
    t2=list(csv.DictReader((ROOT/'outputs/table2_datasets.csv').open(encoding='utf-8')))
    assert len(t2)==142 and {x['configuration'] for x in t2}==set(c)
    for stem in ['figure2_agreement','visual_abstract']:
        with Image.open(ROOT/'outputs'/f'{stem}.png') as a,Image.open(ROOT/'outputs'/f'{stem}.tif') as b:
            assert a.convert('RGB').tobytes()==b.convert('RGB').tobytes()
            assert abs(a.width/300*25.4-170)<.1
            assert all(abs(float(v)-300)<.001 for v in a.info['dpi'])
    with tempfile.TemporaryDirectory(prefix='.verify-',dir=ROOT) as tmp:
        build(Path(tmp))
        for p in Path(tmp).iterdir():assert p.read_bytes()==(ROOT/'outputs'/p.name).read_bytes(),f'Not reproducible: {p.name}'
    rt=ROOT/'outputs/validate_R_table.csv'
    if rt.exists():
        rows=list(csv.DictReader(rt.open(encoding='utf-8')))
        assert len(rows)==164802 and all(x['Result']=='PASS' for x in rows)
        assert len({(x['configuration'],x['quantity'],x['row']) for x in rows})==164802
        assert {x['configuration'] for x in rows}==set(c)
        assert {q:sum(x['quantity']==q for x in rows) for q in {x['quantity'] for x in rows}}=={x['quantity']:int(x['checks_after']) for x in t[:-1] if int(x['checks_after'])}
        for x in rows:
            av,rv=x['App'],x['R'];d=float(x['Difference']);tol=float(x['Tolerance'])
            if av==rv=='null':assert d==0
            elif av in ['TRUE','FALSE'] and rv in ['TRUE','FALSE']:assert d==int(av!=rv)
            else:assert abs(abs(float(av)-float(rv))/max(1,abs(float(rv)))-d)<1e-12
            assert d<=tol
    print('ARCHIVE VERIFIED: hashes, assets, coverage, regenerated tables and 300-dpi images')
if __name__=='__main__':verify()
