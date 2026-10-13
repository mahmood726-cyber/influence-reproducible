import json,math,sys
from pathlib import Path
appfile=sys.argv[1] if len(sys.argv)>1 else 'app.json'
label=sys.argv[2] if len(sys.argv)>2 else 'original'
a=json.loads(Path(appfile).read_text()); r=json.loads(Path('reference.json').read_text())
c=json.loads(Path('corpus.json').read_text())
assert set(a)==set(c),'Browser run incomplete: wait for runner completion'
assert set(r)<=set(c),'Unexpected reference configurations'
assert set(r)==set(c) or '--partial' in sys.argv,'Reference incomplete: use --partial only for diagnostic interim runs'
stats={}; failures=[]
def check(name,x,y,id,row=None,tol=1e-6):
 s=stats.setdefault(name,dict(checks=0,passes=0,max_difference=0,tolerance=tol,worst=None))
 s['checks']+=1
 if x is None or y is None: err=0 if x is None and y is None else float('inf')
 elif isinstance(y,bool): err=int(x!=y)
 else: err=abs(x-y)/max(1,abs(y))
 if err<=tol:s['passes']+=1
 else: failures.append(dict(quantity=name,dataset=id,row=row,app=x,reference=y,difference=err))
 if err>s['max_difference']:s['max_difference']=err;s['worst']=[id,row]
for id,ref in r.items():
 app=a.get(id,{'error':'missing'})
 if 'error' in app or 'error' in ref:
  check('refusal',bool(app.get('error')),bool(ref.get('error')),id,tol=0);continue
 for key in ['mu','seMu','tau2','Q','df']:check('full.'+key,app['full'][key],ref['full'][key],id,tol=1e-9 if key in ['Q','df'] else 1e-6)
 ref_weights=[1/(v+ref['full']['tau2']) for v in c[id]['vi']]
 check('full.swRE',app['full']['swRE'],sum(ref_weights),id)
 for i,w in enumerate(ref_weights):check('full.wRE',app['full']['wRE'][i],w,id,i)
 for i,d in enumerate(app['diag']):
  for ak,rk in [('loo_mu','estimate'),('loo_seMu','se')]:check(ak,d[ak],ref['loo'][rk][i],id,i)
  for sign,key in [(-1,'ci.lb'),(1,'ci.ub')]:check('loo.'+key,d['loo_mu']+sign*1.959963984540054*d['loo_seMu'],ref['loo'][key][i],id,i)
  for ak,rk in [('resid','rstudent'),('dffits','dffits'),('cooksD','cook.d'),('covRatio','cov.r'),('hat','hat')]: check(ak,d[ak],ref['inf'][rk][i],id,i)
  check('flags',app['flags'][i],ref['flags'][i],id,i,tol=0)
  check('weight.percent',100*app['full']['wRE'][i]/app['full']['swRE'],ref['inf']['weight'][i],id,i)
  for k in ['x','y']:
   check('baujat.REML.'+k,app['baujat'][k][i],ref['baujat'][k][i],id,i)
   if label=='original':check('baujat.DL.'+k,app['baujat'][k][i],ref['baujatDL'][k][i],id,i,tol=1e-9)
  for k in ['x','z','resid']:check('radial.'+k,app['radial'][k][i],ref['radial'][k][i],id,i,tol=1e-9)
 check('radial.slope',app['radial']['slope'],ref['radial']['slope'],id,tol=1e-9)
 check('ui.table_rows',app['ui']['tableRows'],len(app['diag'])+1,id,tol=0)
 for i,n in enumerate(app['ui']['plots']):check('ui.plot_nonempty',n>0,True,id,i,tol=0)
total=sum(s['checks'] for s in stats.values());passed=sum(s['passes'] for s in stats.values())
result=dict(configurations=len(r),checks=total,passes=passed,quantities=stats)
Path(f'results-{label}.json').write_text(json.dumps(result,indent=2))
Path(f'failures-{label}.json').write_text(json.dumps(failures,indent=2))
lines=['quantity | pass/checks | maximum normalized difference | tolerance']
for n,s in stats.items():lines.append(f"{n} | {s['passes']}/{s['checks']} | {s['max_difference']:.17g} | {s['tolerance']}")
lines.append(f'{passed}/{total} checks pass')
text='\n'.join(lines);print(text);Path(f'comparison-{label}.txt').write_text(text+'\n')
