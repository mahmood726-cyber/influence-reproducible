# Cache actual metafor deletion fits across leave1out/influence/baujat.
# The original rma.uni function computes every distinct fit. No app numbers enter.
ns<-asNamespace('metafor'); original_rma_uni<-get('rma.uni',ns)
refit_cache<-new.env(parent=emptyenv())
cache_hits<-0L;cache_misses<-0L
cached_rma_uni<-function(...) {
 a<-list(...)
 eligible<-!is.null(a$subset) && is.null(a$weights) && identical(a$test,'z') &&
  (is.null(a$mods) || (is.matrix(a$mods) && ncol(a$mods)==1 && all(a$mods==1))) &&
  (is.null(a$weighted) || isTRUE(a$weighted)) && is.na(a$tau2)
 if(!eligible) return(do.call(original_rma_uni,a))
 idx<-seq_along(a$yi)[a$subset]
 omitted<-setdiff(seq_along(a$yi),idx)
 if(length(omitted)!=1) return(do.call(original_rma_uni,a))
 if(exists('.yi',refit_cache,inherits=FALSE)) {
  stopifnot(identical(get('.yi',refit_cache),as.numeric(a$yi)),identical(get('.vi',refit_cache),as.numeric(a$vi)))
 } else {assign('.yi',as.numeric(a$yi),refit_cache);assign('.vi',as.numeric(a$vi),refit_cache)}
 # Inputs are checked exactly above; serialize the remaining settings without rounding.
 key<-paste(as.integer(serialize(list(omitted=omitted,
   method=a$method,test=a$test,level=a$level,control=a$control),NULL)),collapse=',')
 if(exists(key,refit_cache,inherits=FALSE)) {
  cache_hits<<-cache_hits+1L
  if(cache_hits %% 500L==0L) {cat('CACHE HITS',cache_hits,'MISSES',cache_misses,'\n');flush.console()}
  return(get(key,refit_cache,inherits=FALSE))
 }
 cache_misses<<-cache_misses+1L
 a$outlist<-'beta=beta, se=se, zval=zval, pval=pval, ci.lb=ci.lb, ci.ub=ci.ub, QE=QE, QEp=QEp, tau2=tau2, I2=I2, H2=H2, coef.na=coef.na, vb=vb, s2w=s2w'
 value<-do.call(original_rma_uni,a)
 assign(key,value,refit_cache);value
}
unlockBinding('rma.uni',ns);assign('rma.uni',cached_rma_uni,ns);lockBinding('rma.uni',ns)
