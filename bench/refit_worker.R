library(metafor);source('starts.R')
args<-commandArgs(TRUE);folder<-args[1];worker<-as.integer(args[2]);workers<-as.integer(args[3])
d<-readRDS(file.path(folder,'input.rds'));starts<-seq(1,length(d$yi),by=60)
for(start in starts[(seq_along(starts)-1) %% workers==worker]) {
 file<-file.path(folder,paste0(start,'.rds'))
 if(file.exists(file)) {stopifnot(identical(readRDS(file)$input,d));next}
 ids<-seq.int(start,min(start+59,length(d$yi)))
 values<-lapply(ids,function(i){
  ctl<-d$control
  if(d$method=='REML'){ctl$tau2.init<-start_tau(d$yi[-i],d$vi[-i]);ctl$threshold<-1e-12*max(1,ctl$tau2.init)}
  value<-try(suppressWarnings(metafor::rma.uni(d$yi,d$vi,subset=-i,intercept=TRUE,method=d$method,test=d$test,level=d$level,control=ctl,skipr2=TRUE,
    outlist='beta=beta, se=se, zval=zval, pval=pval, ci.lb=ci.lb, ci.ub=ci.ub, QE=QE, QEp=QEp, tau2=tau2, I2=I2, H2=H2, coef.na=coef.na, vb=vb, s2w=s2w')),silent=TRUE)
  list(i=i,control=ctl,value=value)
 })
 saveRDS(list(input=d,values=values),file)
 cat('REFITS',folder,max(ids),'/',length(d$yi),'\n');flush.console()
}
