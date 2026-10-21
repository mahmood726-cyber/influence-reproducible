# Fresh metafor fits; no saved R reference is used as the numerical oracle.
main <- function() {
  # R_LIBS otherwise precedes R_LIBS_USER and can silently select an older metafor.
  userlibs<-strsplit(Sys.getenv('R_LIBS_USER'),.Platform$path.sep,fixed=TRUE)[[1]]
  .libPaths(c(userlibs[nzchar(userlibs)],.libPaths()))
  for(pkg in c('metafor','metadat','jsonlite','digest')) if(!requireNamespace(pkg,quietly=TRUE)) stop('Missing installed package: ',pkg)
  for(pkg in c('metafor','metadat')) {
    want<-if(pkg=='metafor')'5.2.1' else '1.6.0'
    if(as.character(packageVersion(pkg))!=want)stop('Paper package version required: ',pkg,' ',want,'; found ',packageVersion(pkg))
  }
  if(as.character(getRversion())!='4.6.0')stop('Paper R version required: 4.6.0; found ',getRversion())
  pins <- jsonlite::fromJSON('INPUT_SHA256.json',simplifyVector=FALSE)
  # The manifest must cover exactly the files read or sourced below; an empty or partial manifest verified nothing.
  required <- c('data/corpus.json','results/app-patched.json','bench/starts.R','bench/cache_refits.R','bench/prime_validation.R','bench/validation_worker.R')
  if(!is.list(pins)||is.null(names(pins))||anyDuplicated(names(pins))||!setequal(names(pins),required)||
     !all(vapply(pins,function(h)is.character(h)&&length(h)==1L&&grepl('^[0-9a-f]{64}$',h),TRUE)))stop('Input hash manifest must pin exactly: ',paste(required,collapse=', '))
  for(path in names(pins)) if(!file.exists(path) || digest::digest(file=path,algo='sha256')!=pins[[path]]) stop('SHA-256 mismatch: ',path)
  read <- function(path) jsonlite::fromJSON(path,simplifyVector=FALSE)
  corpus <- read('data/corpus.json');app<-read('results/app-patched.json')
  unique_names<-function(x) !is.null(names(x)) && all(nzchar(names(x))) && !anyDuplicated(names(x))
  check_tree<-function(x) {if(is.list(x)){if(!is.null(names(x)) && !unique_names(x))stop('Duplicate/empty keys');invisible(lapply(x,check_tree))}}
  check_tree(corpus);check_tree(app)
  stopifnot(length(corpus)==142L,length(app)==142L,unique_names(corpus),unique_names(app),setequal(names(corpus),names(app)))
  source('bench/starts.R');source('bench/cache_refits.R');source('bench/prime_validation.R')
  cat(R.version.string,'\nmetafor ',as.character(packageVersion('metafor')),'; paper 5.2-1\n',sep='')
  cat('Recomputed: all numerical quantities and influential flags using fresh metafor fits.\nReplayed: archived UI table row count and four nonempty-plot checks; no browser is run.\n')
  dir.create('outputs',showWarnings=FALSE);pdf(NULL)
  on.exit(dev.off(),add=TRUE)
  chunks<-list()
  numeric_one<-function(x) is.numeric(x)&&length(x)==1L&&is.finite(x)
  field<-function(x,key) {if(!is.list(x)||!(key %in% names(x)))stop('Missing field: ',key);x[[key]]}
  vec<-function(x,k,boolean=FALSE,nullable=FALSE) {
    if(!is.list(x)||length(x)!=k||!all(vapply(x,function(v)if(boolean)is.logical(v)&&length(v)==1L&&!is.na(v) else numeric_one(v)||(nullable&&is.null(v)),TRUE)))stop('Invalid vector shape/type')
    x
  }
  add<-function(id,q,a,r,tol=1e-6,nullable=FALSE,mode='recomputed R') {
    # Lists retain explicit JSON null; absent fields are rejected by field().
    if(!is.list(a))a<-as.list(a);if(!is.list(r))r<-as.list(r)
    stopifnot(length(a)==length(r),length(a)>0L)
    dif<-mapply(function(x,y) {
      if(is.null(x)||is.null(y))return(if(nullable&&is.null(x)&&is.null(y))0 else Inf)
      if(q=='flags'||q=='ui.plot_nonempty')return(if(is.logical(x)&&length(x)==1L&&!is.na(x)&&is.logical(y)&&length(y)==1L&&!is.na(y))as.numeric(x!=y) else Inf)
      if(numeric_one(x)&&numeric_one(y))abs(x-y)/max(1,abs(y)) else Inf
    },a,r)
    val<-function(x)vapply(x,function(v)if(is.null(v))'null' else paste(v,collapse=';'),'')
    chunks[[length(chunks)+1L]]<<-data.frame(configuration=id,quantity=q,row=seq_along(a),App=val(a),R=val(r),Difference=dif,Tolerance=tol,Result=ifelse(dif<=tol,'PASS','FAIL'),Mode=mode)
  }
  for(id in names(corpus)) {
    c<-corpus[[id]];a<-app[[id]];k<-length(field(c,'yi'));stopifnot(k>=3)
    yi<-unlist(vec(field(c,'yi'),k));vi<-unlist(vec(field(c,'vi'),k));stopifnot(all(vi>0))
    rr<-unlist(vec(field(c,'rows'),k));stopifnot(!anyDuplicated(rr),all(rr>0),all(rr==floor(rr)))
    full<-field(a,'full');diag<-field(a,'diag');stopifnot(is.list(diag),length(diag)==k)
    for(q in c('mu','seMu','tau2','Q','df','swRE'))stopifnot(numeric_one(field(full,q)))
    wapp<-unlist(vec(field(full,'wRE'),k));stopifnot(full$swRE>0)
    flags<-vec(field(a,'flags'),k,boolean=TRUE)
    for(d in diag)for(q in c('loo_mu','loo_seMu','resid','dffits','cooksD','covRatio','hat')) {v<-field(d,q);stopifnot(numeric_one(v)||is.null(v))}
    for(kind in c('baujat','radial'))for(q in if(kind=='baujat')c('x','y') else c('x','z','resid'))vec(field(field(a,kind),q),k,nullable=kind=='baujat')
    stopifnot(numeric_one(field(a$radial,'slope')))
    ui<-field(a,'ui');stopifnot(numeric_one(field(ui,'tableRows')))
    plots<-unlist(vec(field(ui,'plots'),4L));stopifnot(all(plots>=0),all(plots==floor(plots)))
    rm(list=ls(refit_cache,all.names=TRUE),envir=refit_cache)
    ctl<-list(tau2.init=start_tau(yi,vi),maxiter=10000,stepadj=1)
    ctl$threshold<-1e-12*max(1,ctl$tau2.init)
    cat('START ',id,' k=',k,'\n',sep='');flush.console()
    res<-metafor::rma(yi,vi,method='REML',test='z',control=ctl)
    prime_validation(res)
    code<-"x$control$tau2.init <- start_tau(x$yi[-i], x$vi[-i]); x$control$threshold <- 1e-12*max(1,x$control$tau2.init)"
    loo<-metafor::leave1out(res,code2=code);inf<-metafor::influence.rma.uni(res,code2=code);bj<-metafor::baujat(res,code2=code)
    fe<-metafor::rma(yi,vi,method='FE',test='z');rad<-metafor::radial(fe)
    values<-list(mu=as.numeric(coef(res)),seMu=res$se,tau2=res$tau2,Q=res$QE,df=k-1)
    for(q in names(values))add(id,paste0('full.',q),full[[q]],values[[q]],if(q %in% c('Q','df'))1e-9 else 1e-6)
    w<-1/(vi+res$tau2);add(id,'full.swRE',full$swRE,sum(w));add(id,'full.wRE',wapp,w)
    # R NA is a genuine undefined diagnostic; convert only here, never on input parsing.
    rvals<-function(x)lapply(x,function(v)if(is.na(v)&&!is.nan(v))NULL else v)
    col<-function(q)lapply(diag,function(d)field(d,q))
    add(id,'loo_mu',col('loo_mu'),rvals(loo$estimate),nullable=TRUE)
    add(id,'loo_seMu',col('loo_seMu'),rvals(loo$se),nullable=TRUE)
    for(sign in c(-1,1)) {
      q<-if(sign==-1)'ci.lb' else 'ci.ub'
      av<-lapply(diag,function(d)if(is.null(d$loo_mu)||is.null(d$loo_seMu))NULL else d$loo_mu+sign*1.959963984540054*d$loo_seMu)
      add(id,paste0('loo.',q),av,rvals(loo[[q]]),nullable=TRUE)
    }
    mapping<-c(resid='rstudent',dffits='dffits',cooksD='cook.d',covRatio='cov.r',hat='hat')
    for(q in names(mapping))add(id,q,col(q),rvals(inf$inf[[mapping[[q]]]]),nullable=TRUE)
    add(id,'flags',flags,as.list(inf$is.infl),0)
    add(id,'weight.percent',100*wapp/full$swRE,inf$inf$weight)
    for(q in c('x','y'))add(id,paste0('baujat.REML.',q),a$baujat[[q]],rvals(bj[[q]]),nullable=TRUE)
    radial<-list(x=rad$x,z=rad$y,resid=rad$y-as.numeric(coef(fe))*rad$x,slope=as.numeric(coef(fe)))
    for(q in names(radial))add(id,paste0('radial.',q),a$radial[[q]],radial[[q]],1e-9)
    add(id,'ui.table_rows',ui$tableRows,k+1,0,mode='replayed archived browser')
    add(id,'ui.plot_nonempty',plots>0,rep(TRUE,4),0,mode='replayed archived browser')
    cat('DONE ',id,' k=',k,'\n',sep='');flush.console()
  }
  tab<-do.call(rbind,chunks);write.csv(tab,'outputs/validate_R_table.csv',row.names=FALSE,na='NA')
  for(q in unique(tab$quantity)) {s<-tab[tab$quantity==q,];cat(sprintf('%s | %d/%d | %.17g | %g\n',q,sum(s$Result=='PASS'),nrow(s),max(s$Difference),s$Tolerance[1]))}
  passed<-sum(tab$Result=='PASS');cat(sprintf('%d/%d checks pass\n',passed,nrow(tab)))
  stopifnot(nrow(tab)==164802L,passed==164802L)
  0L
}
# V1 function body above is byte-identical to v1.0.0.
# Limit the unchanged helper's worker count at load time: parent + one worker.
# This changes scheduling only; pinned helper bytes and fitting arguments stay intact.
v1_environment <- new.env(parent=environment(main))
v1_environment$source <- function(file, ...) {
  result <- base::source(file, ...)
  if (identical(file, 'bench/prime_validation.R')) {
    b <- body(prime_validation)
    stopifnot(identical(b[[3]], quote(workers <- 3L)))
    b[[3]] <- quote(workers <- 1L)
    body(prime_validation) <<- b
  }
  invisible(result)
}
environment(main) <- v1_environment
status <- 0L
if (Sys.getenv('INFLUENCE_V2_ONLY') != '1') {
  status <- tryCatch(main(), error=function(e) {
    cat('Validation failed: ', conditionMessage(e), '\n', sep='', file=stderr()); 1L
  })
} else cat('V1 SKIPPED: INFLUENCE_V2_ONLY=1\n')
if (status == 0L) {
  status <- tryCatch({source('v2/validate.R'); v2_main()}, error=function(e) {
    cat('V2 validation failed: ', conditionMessage(e), '\n', sep='', file=stderr()); 1L
  })
  cat(if (status == 0L) 'V2 REPRODUCED\n' else 'V2 NOT REPRODUCED\n')
} else cat('V2 NOT REPRODUCED: v1 validation failed; v2 not run\n')
quit(save='no', status=status)
