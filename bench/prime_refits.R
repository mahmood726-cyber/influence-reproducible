# Parallel execution of unchanged metafor rma.uni refits, checkpointed in chunks.
# Three local workers; no simulated inputs and no browser output used.
pool_workers<-parallel::makePSOCKcluster(3,rscript=normalizePath('portable-r/bin/Rscript.exe'),outfile='parallel-workers.log')
parallel::clusterEvalQ(pool_workers,{library(metafor);source('starts.R');NULL})
prime_refits<-function(model,dataset_id) {
 d<-list(yi=as.numeric(model$yi),vi=as.numeric(model$vi),method=model$method,test=model$test,level=model$level,control=model$control)
 assign('.yi',d$yi,refit_cache);assign('.vi',d$vi,refit_cache)
 subdir<-file.path('refit-checkpoints',paste0(match(dataset_id,names(corpus)),'-',d$method))
 dir.create(subdir,recursive=TRUE,showWarnings=FALSE)
 for(start in seq(1,length(d$yi),by=60)) {
  ids<-seq.int(start,min(start+59,length(d$yi)))
  file<-file.path(subdir,paste0(start,'.rds'))
  if(file.exists(file)) {vals<-readRDS(file);stopifnot(identical(vals$input,d));values<-vals$values}
  else {
   values<-parallel::parLapply(pool_workers,ids,function(i,d){
    ctl<-d$control
    if(d$method=='REML') {ctl$tau2.init<-start_tau(d$yi[-i],d$vi[-i]);ctl$threshold<-1e-12*max(1,ctl$tau2.init)}
    val<-try(suppressWarnings(metafor::rma.uni(d$yi,d$vi,subset=-i,intercept=TRUE,method=d$method,test=d$test,level=d$level,control=ctl,skipr2=TRUE,
     outlist='beta=beta, se=se, zval=zval, pval=pval, ci.lb=ci.lb, ci.ub=ci.ub, QE=QE, QEp=QEp, tau2=tau2, I2=I2, H2=H2, coef.na=coef.na, vb=vb, s2w=s2w')),silent=TRUE)
    list(i=i,control=ctl,value=val)
   },d=d)
   saveRDS(list(input=d,values=values),file)
  }
  for(v in values) {
   key<-paste(as.integer(serialize(list(omitted=as.integer(v$i),method=d$method,test=d$test,level=d$level,control=v$control),NULL)),collapse=',')
   if(!inherits(v$value,'try-error')) assign(key,v$value,refit_cache)
  }
  cat('REFITS',dataset_id,d$method,max(ids),'/',length(d$yi),'\n');flush.console()
 }
}
