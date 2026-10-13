# File-based local workers: no sockets or external network.
prime_refits<-function(model,dataset_id,worker_limit=3) {
 d<-list(yi=as.numeric(model$yi),vi=as.numeric(model$vi),method=model$method,test=model$test,level=model$level,control=model$control)
 assign('.yi',d$yi,refit_cache);assign('.vi',d$vi,refit_cache)
 subdir<-file.path('refit-checkpoints',paste0(match(dataset_id,names(corpus)),'-',d$method))
 dir.create(subdir,recursive=TRUE,showWarnings=FALSE)
 saveRDS(d,file.path(subdir,'input.rds'))
 starts<-seq(1,length(d$yi),by=60);workers<-min(worker_limit,length(starts))
 status<-system2(Sys.which('python'),c('prime_compute.py',subdir,workers))
 if(status!=0) stop('Refit subprocess failure; see worker logs')
 for(start in starts) {
  vals<-readRDS(file.path(subdir,paste0(start,'.rds')));stopifnot(identical(vals$input,d))
  for(v in vals$values) {
   key<-paste(as.integer(serialize(list(omitted=as.integer(v$i),method=d$method,test=d$test,level=d$level,control=v$control),NULL)),collapse=',')
   if(!inherits(v$value,'try-error')) assign(key,v$value,refit_cache)
  }
 }
 cat('REFITS',dataset_id,d$method,length(d$yi),'/',length(d$yi),'\n');flush.console()
}
