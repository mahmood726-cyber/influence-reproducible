"""Strict primary paper contract; never equate absent fields with null."""
import json, math
from pathlib import Path

def unique(pairs):
    out={}
    for key,value in pairs:
        if key in out: raise ValueError('Duplicate key: '+key)
        out[key]=value
    return out
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),object_pairs_hook=unique,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite '+s)))
def finite(x): return type(x) in (int,float) and math.isfinite(x)
def vector(x,k,boolean=False,nullable=False):
    assert isinstance(x,list) and len(x)==k, 'Array cardinality'
    assert all(type(v) is bool if boolean else (finite(v) or (nullable and v is None)) for v in x), 'Array type'
def shape(c,a,r):
    k=len(c['yi']);assert k>=3
    vector(c['yi'],k);vector(c['vi'],k);assert all(v>0 for v in c['vi'])
    vector(c['rows'],k);assert len(set(c['rows']))==k and all(type(v) is int and v>0 for v in c['rows'])
    for q in ['mu','seMu','tau2','Q','df']:assert finite(a['full'][q]) and finite(r['full'][q]),q
    assert finite(a['full']['swRE']) and a['full']['swRE']>0
    vector(a['full']['wRE'],k)
    assert isinstance(a['diag'],list) and len(a['diag'])==k
    for d in a['diag']:
        for q in ['loo_mu','loo_seMu','resid','dffits','cooksD','covRatio','hat']:
            assert q in d and (finite(d[q]) or d[q] is None),q
    vector(a['flags'],k,boolean=True);vector(r['flags'],k,boolean=True)
    for q in ['estimate','se','ci.lb','ci.ub']:vector(r['loo'][q],k,nullable=True)
    for q in ['rstudent','dffits','cook.d','cov.r','hat','weight']:vector(r['inf'][q],k,nullable=True)
    for obj in [a['baujat'],r['baujat']]:
        for q in ['x','y']:vector(obj[q],k,nullable=True)
    for obj in [a['radial'],r['radial']]:
        for q in ['x','z','resid']:vector(obj[q],k)
        assert finite(obj['slope'])
    assert type(a['ui']['tableRows']) is int
    vector(a['ui']['plots'],4);assert all(type(n) is int and n>=0 for n in a['ui']['plots'])
    return k
def compare(corpus,app,reference,original=False):
    assert len(corpus)==142 and set(corpus)==set(app)==set(reference),'Exact coverage required'
    rows=[]
    def check(id,q,a,r,i=None,tol=1e-6,nullable=False):
        if q=='flags' or q=='ui.plot_nonempty':
            valid=type(a) is bool and type(r) is bool;d=int(a!=r) if valid else math.inf
        elif a is None or r is None:d=0 if nullable and a is None and r is None else math.inf
        else:d=abs(a-r)/max(1,abs(r)) if finite(a) and finite(r) else math.inf
        rows.append(dict(configuration=id,quantity=q,row=i,app=a,reference=r,difference=d,tolerance=tol,passed=d<=tol))
    for id,c in corpus.items():
        a=app[id];r=reference[id];k=shape(c,a,r)
        if original:
            for q in ['x','y']:vector(r['baujatDL'][q],k,nullable=True)
        for q in ['mu','seMu','tau2','Q','df']:check(id,'full.'+q,a['full'][q],r['full'][q],tol=1e-9 if q in ['Q','df'] else 1e-6)
        w=[1/(v+r['full']['tau2']) for v in c['vi']]
        check(id,'full.swRE',a['full']['swRE'],sum(w))
        for i,d in enumerate(a['diag']):
            check(id,'full.wRE',a['full']['wRE'][i],w[i],i)
            for aq,rq in [('loo_mu','estimate'),('loo_seMu','se')]:check(id,aq,d[aq],r['loo'][rq][i],i,nullable=True)
            for sign,q in [(-1,'ci.lb'),(1,'ci.ub')]:
                val=None if d['loo_mu'] is None or d['loo_seMu'] is None else d['loo_mu']+sign*1.959963984540054*d['loo_seMu']
                check(id,'loo.'+q,val,r['loo'][q][i],i,nullable=True)
            for aq,rq in [('resid','rstudent'),('dffits','dffits'),('cooksD','cook.d'),('covRatio','cov.r'),('hat','hat')]:check(id,aq,d[aq],r['inf'][rq][i],i,nullable=True)
            check(id,'flags',a['flags'][i],r['flags'][i],i,tol=0)
            check(id,'weight.percent',100*a['full']['wRE'][i]/a['full']['swRE'],r['inf']['weight'][i],i)
            for q in ['x','y']:
                check(id,'baujat.REML.'+q,a['baujat'][q][i],r['baujat'][q][i],i,nullable=True)
                if original:check(id,'baujat.DL.'+q,a['baujat'][q][i],r['baujatDL'][q][i],i,tol=1e-9,nullable=True)
            for q in ['x','z','resid']:check(id,'radial.'+q,a['radial'][q][i],r['radial'][q][i],i,tol=1e-9)
        check(id,'radial.slope',a['radial']['slope'],r['radial']['slope'],tol=1e-9)
        check(id,'ui.table_rows',a['ui']['tableRows'],k+1,tol=0)
        for i,n in enumerate(a['ui']['plots']):check(id,'ui.plot_nonempty',n>0,True,i,tol=0)
    assert len(rows)==(183990 if original else 164802),'Exact check coverage'
    return rows
def summarize(rows):
    out={}
    for row in rows:
        s=out.setdefault(row['quantity'],dict(checks=0,passed=0,max_difference=0,tolerance=row['tolerance']))
        s['checks']+=1;s['passed']+=row['passed'];s['max_difference']=max(s['max_difference'],row['difference'])
    return out
