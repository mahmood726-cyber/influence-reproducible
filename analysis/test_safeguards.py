"""Negative controls for coverage, shape, byte integrity and publication outputs."""
import copy,json,hashlib,subprocess,shutil,tempfile
from pathlib import Path
import pytest
from checks import read,compare
from make_outputs import ROOT

@pytest.fixture(scope='module')
def records():return (read(ROOT/'data/corpus.json'),read(ROOT/'results/app-patched.json'),read(ROOT/'results/reference.json'))

@pytest.mark.parametrize('target',['corpus','app','reference'])
@pytest.mark.parametrize('operation',['missing','extra','renamed'])
def test_exact_coverage(records,target,operation):
    data=copy.deepcopy(records);x=data[['corpus','app','reference'].index(target)];key=next(iter(x))
    if operation=='missing':del x[key]
    elif operation=='extra':x['unexpected']=x[key]
    else:x['unexpected']=x.pop(key)
    with pytest.raises(AssertionError):compare(*data)

@pytest.mark.parametrize('raw',['{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}','{"a":-Infinity}'])
def test_json_rejects_duplicates_nonfinite(raw):
    with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as tmp:
        p=Path(tmp)/'bad.json';p.write_text(raw,encoding='utf-8')
        with pytest.raises(ValueError):read(p)

@pytest.mark.parametrize('mutation',[
    'missing_field','both_missing','string','boolean_number','nan','infinity','null_full','both_null_full',
    'short_vector','long_vector','non_boolean_flag','duplicate_row','zero_variance','missing_plot','null_radial'])
def test_record_shape(records,mutation):
    c,a,r=copy.deepcopy(records);id=next(iter(c))
    if mutation=='missing_field':del a[id]['diag'][0]['resid']
    elif mutation=='both_missing':del a[id]['full']['mu'];del r[id]['full']['mu']
    elif mutation=='string':a[id]['full']['mu']='1'
    elif mutation=='boolean_number':a[id]['full']['mu']=True
    elif mutation=='nan':a[id]['diag'][0]['dffits']=float('nan')
    elif mutation=='infinity':r[id]['inf']['dffits'][0]=float('inf')
    elif mutation=='null_full':a[id]['full']['mu']=None
    elif mutation=='both_null_full':a[id]['full']['mu']=r[id]['full']['mu']=None
    elif mutation=='short_vector':r[id]['loo']['se'].pop()
    elif mutation=='long_vector':a[id]['diag'].append(a[id]['diag'][0])
    elif mutation=='non_boolean_flag':a[id]['flags'][0]=1
    elif mutation=='duplicate_row':c[id]['rows'][1]=c[id]['rows'][0]
    elif mutation=='zero_variance':c[id]['vi'][0]=0
    elif mutation=='missing_plot':a[id]['ui']['plots'].pop()
    elif mutation=='null_radial':a[id]['radial']['x'][0]=None
    with pytest.raises((AssertionError,KeyError)):compare(c,a,r)

def test_null_is_not_missing(records):
    c,a,r=copy.deepcopy(records);id=next(iter(c))
    # An explicitly unavailable deleted fit may be null on both sides.
    a[id]['diag'][0]['resid']=r[id]['inf']['rstudent'][0]=None
    rows=compare(c,a,r);assert all(x['passed'] for x in rows)
    del a[id]['diag'][0]['resid']
    with pytest.raises((AssertionError,KeyError)):compare(c,a,r)

def test_numeric_failure_is_not_silently_dropped(records):
    c,a,r=copy.deepcopy(records);id=next(iter(c));a[id]['diag'][0]['dffits']+=1
    rows=compare(c,a,r);assert len(rows)==164802 and sum(not x['passed'] for x in rows)==1

@pytest.mark.parametrize('fault',['short','long','wrong_type'])
def test_before_only_DL_controls_require_exact_shape(records,fault):
    c,_,r=copy.deepcopy(records);a=read(ROOT/'results/app.json');id=next(iter(c))
    if fault=='short':r[id]['baujatDL']['x'].pop()
    elif fault=='long':r[id]['baujatDL']['x'].append(0)
    else:r[id]['baujatDL']['x'][0]='0'
    with pytest.raises(AssertionError):compare(c,a,r,original=True)

@pytest.mark.parametrize('mutation',['hash','missing','extra','duplicate','shape','wrong_type','null_full'])
def test_R_refuses_bad_evidence_before_fitting(records,mutation):
    rscript=shutil.which('Rscript')
    assert rscript,'Rscript required for validator negative controls'
    work=ROOT/'.validate-work';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        tmp=Path(tmp)
        for name in ['validate.R','INPUT_SHA256.json',*read(ROOT/'INPUT_SHA256.json')]:
            p=tmp/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
        p=tmp/'results/app-patched.json';a=copy.deepcopy(records[1]);id=next(iter(a))
        if mutation=='hash':p.write_bytes(p.read_bytes()+b' ')
        else:
            if mutation=='missing':del a[id]
            elif mutation=='extra':a['unexpected']=a[id]
            elif mutation=='shape':a[id]['diag'].pop()
            elif mutation=='wrong_type':a[id]['flags'][0]=1
            elif mutation=='null_full':a[id]['full']['mu']=None
            if mutation=='duplicate':
                text=json.dumps(a);text=text[:-1]+','+json.dumps(id)+':'+json.dumps(a[id])+'}'
            else:text=json.dumps(a)
            p.write_text(text,encoding='utf-8')
            pins=read(tmp/'INPUT_SHA256.json');pins['results/app-patched.json']=hashlib.sha256(p.read_bytes()).hexdigest()
            (tmp/'INPUT_SHA256.json').write_text(json.dumps(pins),encoding='utf-8')
        result=subprocess.run([rscript,'validate.R'],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        assert result.returncode!=0 and 'Validation failed:' in result.stdout,result.stdout
        assert 'DONE ' not in result.stdout and not (tmp/'outputs/validate_R_table.csv').exists()
        if mutation=='hash':assert 'SHA-256 mismatch' in result.stdout

@pytest.mark.parametrize('name',['outputs/table1_by_quantity.csv','outputs/numbers.json','outputs/figure2_agreement.png','app/shared/ma-core.js'])
def test_archive_rejects_changed_outputs_or_assets(name):
    from verify_archive import verify
    p=ROOT/name;original=p.read_bytes()
    try:
        p.write_bytes(b'corrupted evidence')
        with pytest.raises((AssertionError,ValueError,KeyError,OSError)):verify()
    finally:p.write_bytes(original)

def test_archive_baseline_verifies():
    from verify_archive import verify
    verify()

def test_R_refuses_wrong_package_version_before_fitting():
    result=subprocess.run([shutil.which('Rscript'),'-e',"packageVersion <- function(pkg) package_version('0.0.0'); source('validate.R')"],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
    assert result.returncode!=0 and 'Paper package version required' in result.stdout
    assert 'START ' not in result.stdout

def test_R_nan_is_not_converted_to_undefined_null():
    code="line <- grep('^    rvals<-function',readLines('validate.R'),value=TRUE); stopifnot(length(line)==1); eval(parse(text=line)); x<-rvals(c(NA_real_,NaN,Inf,1)); stopifnot(is.null(x[[1]]),is.nan(x[[2]]),is.infinite(x[[3]]),identical(x[[4]],1)); cat('R NA/NaN/Infinity distinction PASS\\n')"
    result=subprocess.run([shutil.which('Rscript'),'-e',code],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
    assert result.returncode==0 and 'distinction PASS' in result.stdout,result.stdout

@pytest.mark.parametrize('fault',['input','missing','duplicate','worker'])
def test_fresh_worker_protocol_refuses_corruption(fault):
    # Mock only the subprocess transport: real corpus inputs, deliberately invalid
    # chunk/status records, and the unmodified production protocol validator.
    work=ROOT/'.validate-work';work.mkdir(exist_ok=True)
    script=r'''
source('bench/prime_validation.R')
c<-jsonlite::fromJSON('data/corpus.json',simplifyVector=FALSE)[['dat.bakdash2021::ZCOR stored']]
model<-list(yi=unlist(c$yi),vi=unlist(c$vi),method='REML',test='z',level=95,control=list())
refit_cache<-new.env(parent=emptyenv())
fault<-commandArgs(TRUE)[1]
system2<-function(command,args,...) {
  unquote<-function(x)if(substr(x,1,1) %in% c('"',"'"))substr(x,2,nchar(x)-1) else x
  folder<-unquote(args[4]);i<-as.integer(args[5]);status<-unquote(args[7])
  if(i==1L) {
    d<-readRDS(file.path(folder,'input.rds'));ids<-seq_along(d$yi)
    if(fault=='input')d$yi[1]<-d$yi[1]+1
    if(fault=='missing')ids<-ids[-1]
    if(fault=='duplicate')ids[2]<-ids[1]
    values<-lapply(ids,function(i)list(i=i,control=d$control,value=list()))
    saveRDS(list(input=d,values=values),file.path(folder,'chunk-1.rds'))
  }
  writeLines(if(fault=='worker')'1' else '0',status);0L
}
refused<-tryCatch({prime_validation(model);FALSE},error=function(e){cat('EXPECTED REFUSAL:',conditionMessage(e),'\n');TRUE})
stopifnot(refused)
'''
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        p=Path(tmp)/'negative.R';p.write_text(script,encoding='utf-8')
        result=subprocess.run([shutil.which('Rscript'),str(p),fault],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        assert result.returncode==0 and 'EXPECTED REFUSAL:' in result.stdout,result.stdout
