# Exact metafor deletion fits, fresh per run; never reads archived app outputs.
args<-commandArgs(TRUE);root<-args[1];folder<-args[2];worker<-as.integer(args[3]);workers<-as.integer(args[4]);statusfile<-args[5]
writeLines(as.character(Sys.getpid()),file.path(folder,paste0(worker,'.pid')))
main<-function() {
  userlibs<-strsplit(Sys.getenv('R_LIBS_USER'),.Platform$path.sep,fixed=TRUE)[[1]]
  .libPaths(c(userlibs[nzchar(userlibs)],.libPaths()))
  library(metafor)
  stopifnot(as.character(packageVersion('metafor'))=='5.2.1',as.character(packageVersion('metadat'))=='1.6.0',as.character(getRversion())=='4.6.0')
  source(file.path(root,'bench/starts.R'))
  d<-readRDS(file.path(folder,'input.rds'))
  starts<-seq.int(1L,length(d$yi),by=60L)
  for(start in starts[(seq_along(starts)-1L)%%workers==worker-1L]) {
    ids<-seq.int(start,min(start+59L,length(d$yi)))
    values<-lapply(ids,function(i) {
      ctl<-d$control;ctl$tau2.init<-start_tau(d$yi[-i],d$vi[-i]);ctl$threshold<-1e-12*max(1,ctl$tau2.init)
      val<-metafor::rma.uni(d$yi,d$vi,subset=-i,intercept=TRUE,method=d$method,test=d$test,level=d$level,control=ctl,skipr2=TRUE,
        outlist='beta=beta, se=se, zval=zval, pval=pval, ci.lb=ci.lb, ci.ub=ci.ub, QE=QE, QEp=QEp, tau2=tau2, I2=I2, H2=H2, coef.na=coef.na, vb=vb, s2w=s2w')
      list(i=i,control=ctl,value=val)
    })
    # Publish only complete chunks; the master never opens a partly written RDS.
    target<-file.path(folder,paste0('chunk-',start,'.rds'));temp<-paste0(target,'.tmp')
    saveRDS(list(input=d,values=values),temp);stopifnot(file.rename(temp,target))
    cat('DONE DELETIONS ',max(ids),'/',length(d$yi),'\n',sep='');flush.console()
  }
  0L
}
status<-tryCatch(main(),error=function(e){cat(conditionMessage(e),'\n',file=stderr());1L})
writeLines(as.character(status),statusfile)
quit(save='no',status=status)
