"""Regenerate every publication number from strict source-backed comparisons."""
from pathlib import Path
import csv,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image
from checks import read,compare,summarize
ROOT=Path(__file__).resolve().parents[1]
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def csvwrite(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def save(fig,out,name):
    for ext in ['png','tif']:fig.savefig(out/(name+'.'+ext),dpi=300)
    plt.close(fig)
def build(out):
    out.mkdir(exist_ok=True,parents=True)
    c=read(ROOT/'data/corpus.json');r=read(ROOT/'results/reference.json')
    a=read(ROOT/'results/app-patched.json');old=read(ROOT/'results/app.json')
    after=compare(c,a,r);before=compare(c,old,r,True)
    new=summarize(after);prev=summarize(before)
    n=dict(configurations=len(c),effect_rows=sum(len(x['yi']) for x in c.values()),checks=len(after),passed=sum(x['passed'] for x in after),before_checks=len(before),before_passed=sum(x['passed'] for x in before))
    assert n==read(ROOT/'expected/paper_values.json')
    for stats,name in [(new,'patched'),(prev,'original')]:
        ledger=read(ROOT/f'results/results-{name}.json')
        for q,s in stats.items():
            t=ledger['quantities'][q]
            assert (s['checks'],s['passed'],s['max_difference'],s['tolerance'])==(t['checks'],t['passes'],t['max_difference'],t['tolerance']),(name,q)
    table=[]
    for q,s in prev.items():
        t=new.get(q)
        table.append(dict(quantity=q,checks_before=s['checks'],passed_before=s['passed'],checks_after=t['checks'] if t else 0,passed_after=t['passed'] if t else 0,largest_difference_before=s['max_difference'],largest_difference_after=t['max_difference'] if t else '',tolerance=s['tolerance'],scope='primary' if t else 'before-only DL control'))
    table.append(dict(quantity='TOTAL',checks_before=n['before_checks'],passed_before=n['before_passed'],checks_after=n['checks'],passed_after=n['passed'],largest_difference_before='',largest_difference_after='',tolerance='quantity-specific',scope='Before includes 19188 additional DL Baujat control checks; after is the primary REML comparison'))
    csvwrite(out/'table1_by_quantity.csv',table)
    datasets=[dict(configuration=id,dataset=x['dataset'],effect_definition=x['definition'],k=len(x['yi']),flagged_studies=sum(a[id]['flags']),flagged_source_rows=';'.join(str(row) for row,flag in zip(x['rows'],a[id]['flags']) if flag)) for id,x in c.items()]
    csvwrite(out/'table2_datasets.csv',datasets)
    claims={key:dict(value=v,source='data/corpus.json' if key in ['configurations','effect_rows'] else 'results/reference.json + results/app-patched.json + results/app.json',transformation='strict comparison; before includes DL controls' if 'checks' in key or 'passed' in key else 'count configurations / sum effect rows',validation='asserted against expected/paper_values.json') for key,v in n.items()}
    for key,v in [('datasets_used',len({x['dataset'] for x in c.values()})),('datasets_enumerated',len(list(csv.DictReader((ROOT/'data/dataset-inventory.csv').open(encoding='utf-8')))))]:claims[key]=dict(value=v,source='data/corpus.json + data/dataset-inventory.csv',transformation='count unique dataset names / inventory rows',validation='inventory reconciliation in verify_archive.py')
    for q,s in new.items():claims['max_'+q]=dict(value=s['max_difference'],source='results/reference.json + results/app-patched.json',transformation='max absolute difference / max(1,abs(R)); exact flags/UI',validation='compared with results/results-patched.json')
    dump(out/'numbers.json',claims)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8})
    fig,ax=plt.subplots(figsize=(170/25.4,7.8))
    qs=list(prev)
    for j,q in enumerate(qs):
        # Every check is plotted (zero differences are floored only for display).
        good=[math.log10(max(x['difference'],1e-16)) for x in after if x['quantity']==q]
        bad=[math.log10(max(x['difference'],1e-16)) for x in before if x['quantity']==q and not x['passed']]
        ax.scatter(good,[j+.10]*len(good),s=5,color='#24658a',alpha=.35,rasterized=True)
        ax.scatter(bad,[j-.10]*len(bad),s=9,marker='x',color='#bd4c2f',alpha=.6,rasterized=True)
        tol=prev[q]['tolerance']
        if tol:ax.plot([math.log10(tol)]*2,[j-.35,j+.35],color='#333',ls='--',lw=1)
    ax.scatter([],[],s=12,color='#24658a',label='After (all checks)');ax.scatter([],[],s=16,marker='x',color='#bd4c2f',label='Before failures')
    ax.set_yticks(range(len(qs)),qs);ax.invert_yaxis();ax.set_xlim(-16.5,1.3)
    ax.set_xlabel('log10 normalized difference (zeros / <1e-16 at -16)')
    ax.set_title('Influence diagnostics: agreement with metafor',fontsize=10)
    ax.grid(axis='x',alpha=.2);ax.legend(loc='lower right')
    fig.text(.5,.02,'Dashed segments: quantity tolerance. Flags and UI require exact equality.\nDL controls occur only before the fix; all primary after-fix checks pass.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.06,1,1));save(fig,out,'figure2_agreement')
    fig=plt.figure(figsize=(170/25.4,3.65))
    boxes=[('Problem','Study influence\ncan change a\nmeta-analysis\nconclusion.'),('Tool','REML influence\ndiagnostics, LOO,\nBaujat and radial\nplots in a browser.'),('Validation',f'{n["configurations"]} configurations\n{n["effect_rows"]:,} effect rows\nAgainst R package\nmetafor.'),('Result',f'{n["passed"]:,} of\n{n["checks"]:,} checks pass\n(after 3 fixes)')]
    for i,(head,body) in enumerate(boxes):
        x=.02+i*.245
        fig.patches.append(FancyBboxPatch((x,.25),.22,.52,boxstyle='round,pad=0.008',transform=fig.transFigure,facecolor=['#f4ece8','#e8f0f7','#eaf4ec','#fdf6e3'][i],edgecolor='#999'))
        fig.text(x+.11,.70,head,ha='center',weight='bold',fontsize=10);fig.text(x+.11,.49,body,ha='center',va='center',fontsize=8,linespacing=1.6)
    fig.text(.5,.89,'Influence diagnostics for meta-analysis in the browser',ha='center',fontsize=11,weight='bold')
    fig.text(.5,.13,'Intercept-only REML. Arithmetic validation, not a clinical analysis.',ha='center',fontsize=8)
    fig.text(.5,.07,'GOSH and unexposed p-values / heterogeneity outputs are outside this contract.',ha='center',fontsize=8)
    save(fig,out,'visual_abstract')
    sizes={}
    for p in sorted(out.iterdir()):
        if p.suffix in ['.png','.tif']:
            with Image.open(p) as im:sizes[p.name]=dict(width_pixels=im.width,height_pixels=im.height,dpi=list(map(float,im.info['dpi'])))
    dump(out/'sizes.json',sizes)
    (out/'reproduction_report.md').write_text(f'''Recomputed from archived inputs: {n['passed']}/{n['checks']} after and {n['before_passed']}/{n['before_checks']} before.\n\nThe before denominator includes 19,188 DL Baujat controls; the after denominator is the complete primary REML comparison. Per-quantity totals are independently matched against the source ledgers. Table 2 identifies flagged source-row positions within each prepared configuration; these are not universal study identifiers.\n\nFigures are 170 mm wide at 300 dpi; all text is at least 8 pt. Figure 2 plots every check's log10 normalized difference; values below 1e-16 are displayed at -16. Red crosses mark before-fix failures. Exact flags and UI counts have zero tolerance. DL-only rows have no after points.\n\nThese outputs regenerate the archived comparison. Run Rscript validate.R for fresh R fits; the five UI checks per configuration replay archived browser evidence. No manuscript draft or release certification is included.\n''',encoding='utf-8',newline='\n')
    return n
if __name__=='__main__':
    n=build(ROOT/'outputs');print(f"OUTPUTS: {n['passed']}/{n['checks']} after; {n['before_passed']}/{n['before_checks']} before")
