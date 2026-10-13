library(metafor)
source('json.R')
source('starts.R')
corpus<-readRDS('corpus.rds')
dir.create('reference-parts',showWarnings=FALSE)
meta<-list(R=R.version.string,metafor=as.character(packageVersion('metafor')),metadat=as.character(packageVersion('metadat')),
 method='REML',test='z',control=list(threshold=1e-12,maxiter=10000,stepadj=1),threshold_rule='1e-12 * max(1, starting tau2); avoids sub-ULP thresholds for large variance scales',starting_values='Independent scalar score; confirmed by unmodified metafor Fisher scoring')
write_json(meta,'reference-environment.json')
pdf('reference-plots.pdf')
for(id in names(corpus)) {
 f<-file.path('reference-parts',paste0(match(id,names(corpus)),'.json'))
 if(file.exists(f) && startsWith(readLines(f,n=1),paste0('{',json(id),':'))) next
 c<-corpus[[id]]; yi<-c$yi; vi<-c$vi; warns<-character()
 cat('START',match(id,names(corpus)),id,length(yi),'\n'); flush.console()
 result<-tryCatch(withCallingHandlers({
  ctl<-meta$control; ctl$tau2.init<-start_tau(yi,vi);ctl$threshold<-1e-12*max(1,ctl$tau2.init)
  res<-rma(yi,vi,method='REML',test='z',control=ctl)
  code<-"x$control$tau2.init <- start_tau(x$yi[-i], x$vi[-i]); x$control$threshold <- 1e-12*max(1,x$control$tau2.init)"
  loo<-leave1out(res,code2=code); inf<-influence(res,code2=code); bj<-baujat(res,code2=code)
  dl<-rma(yi,vi,method='DL',test='z'); bdl<-baujat(dl)
  fe<-rma(yi,vi,method='FE',test='z')
  list(full=list(mu=as.numeric(coef(res)),seMu=res$se,ciLo=res$ci.lb,ciHi=res$ci.ub,p=res$pval,tau2=res$tau2,Q=res$QE,I2=res$I2,Qp=res$QEp,df=res$k-1),
   loo=as.list(loo),inf=as.list(inf$inf),flags=inf$is.infl,dfbetas=as.list(inf$dfbs),
   baujat=as.list(bj),baujatDL=as.list(bdl),
   radial=list(x=1/sqrt(vi),z=yi/sqrt(vi),slope=as.numeric(coef(fe)),resid=(yi-as.numeric(coef(fe)))/sqrt(vi)))
 },warning=function(w){warns<<-c(warns,conditionMessage(w));invokeRestart('muffleWarning')}),error=function(e)list(error=conditionMessage(e)))
 result$warnings<-warns
 write_json(setNames(list(result),id),f)
 cat('DONE',id,if(is.null(result$error))'OK' else result$error,'\n'); flush.console()
}
dev.off()
files<-file.path('reference-parts',paste0(seq_along(corpus),'.json'))
writeLines(paste0('{',paste(vapply(files,function(f){s<-paste(readLines(f),collapse='');substr(s,2,nchar(s)-1)},''),collapse=','),'}'),'reference.json')
cat('REFERENCE',length(corpus),'configurations\n')
