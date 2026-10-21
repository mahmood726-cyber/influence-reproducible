"""Verify 1.1.0 inventories, release identifiers and byte preservation, without refitting or rendering."""
from refresh_hashes import ROOT, sources, sha
from validate import read, require, inventory

RELEASE='v1.8.0'
RELEASE_COMMIT='1cb3f8409c7af75ed41f7e1811f9c502f900fc79'
RELEASE_DOI='10.5281/zenodo.23515177'
V1_ENGINE_COMMIT='c6b8912c951a107a04228b9b52004d7ecc0d20e5'

def main():
    require(read(ROOT/'SOURCE_SHA256.json')=={p.relative_to(ROOT).as_posix():sha(p) for p in sources()},'Release source inventory/hash mismatch')
    pins=read(ROOT/'v2/provenance/v1-files-sha256.json')
    changed={'README.md','CHANGELOG.md','CITATION.cff','.zenodo.json','SOURCE_SHA256.json','validate.R'}
    for p,h in pins.items():
        candidate=ROOT/('v2/provenance/v1-release/'+p if p in changed else p)
        require(sha(candidate)==h,'V1 preservation failure: '+p)
    print(f'V1 PRESERVED {len(pins)-len(changed)}/{len(pins)-len(changed)} original files; {len(changed)}/{len(changed)} release-file originals retained')
    original=(ROOT/'v2/provenance/v1-release/validate.R').read_bytes().split(b'status<-tryCatch(main()')[0]
    require((ROOT/'validate.R').read_bytes().startswith(original),'V1 function body changed')
    require(read(ROOT/'.zenodo.json')['version']=='1.1.0' and 'version: 1.1.0' in (ROOT/'CITATION.cff').read_text(),'Release metadata version')
    require('[ARCHIVE v1.1.0 DOI PENDING]' in (ROOT/'CITATION.cff').read_text(),'DOI pending marker')
    # The allmeta release identifiers must be filled in, with no unfilled token left behind.
    for name in ['README.md','CITATION.cff','.zenodo.json','CHANGELOG.md','v2/README.md']:
        text=(ROOT/name).read_text(encoding='utf-8')
        require('<ALLMETA_RELEASE' not in text,'Unfilled release token: '+name)
        require(RELEASE in text and RELEASE_DOI in text,'allmeta '+RELEASE+' tag/DOI missing: '+name)
    require((ROOT/'RELEASE_EQUIVALENCE.md').is_file(),'Release equivalence record missing: RELEASE_EQUIVALENCE.md')
    eq=(ROOT/'RELEASE_EQUIVALENCE.md').read_text(encoding='utf-8')
    for needed in [RELEASE_COMMIT,RELEASE_DOI,V1_ENGINE_COMMIT,'byte-identical','ENGINE','NON-ENGINE']:
        require(needed in eq,'Release equivalence record incomplete: '+needed)
    repin=read(ROOT/'v2/provenance/repin-v1.8.0.json')
    require(repin['allmeta_release_commit']==RELEASE_COMMIT and repin['allmeta_release_doi']==RELEASE_DOI,'Re-pin record release mismatch')
    require(repin['counts']['files']==len(read(ROOT/'v2/app/app-sha256.json')),'Re-pin record file count')
    scope=read(ROOT/'v2/provenance/engine-scope-c6b8912.json')
    require(scope['from_commit']==V1_ENGINE_COMMIT and scope['to_commit']==RELEASE_COMMIT,'Engine-scope record commit mismatch')
    require(len(scope['files'])==scope['counts']['files'] and scope['counts']['engine']+scope['counts']['non_engine']==scope['counts']['files'],'Engine-scope record incomplete')
    require(all(f['classification'] in ('ENGINE','NON-ENGINE') for f in scope['files']),'Engine-scope classification missing')
    print(f'RELEASE IDENTIFIERS {RELEASE} / {RELEASE_DOI} filled in 5/5 files; equivalence record present')
    print(f"ENGINE SCOPE {scope['counts']['files']}/{scope['counts']['files']} files classified "
          f"({scope['counts']['engine']} ENGINE, {scope['counts']['non_engine']} NON-ENGINE)")
    inventory()
    print('V1 FUNCTION BODY 1/1 byte-identical')
    print('RELEASE VERIFIED')
if __name__=='__main__':main()
