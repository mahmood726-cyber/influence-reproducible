# Independent scalar score used ONLY as a starting value for unmodified metafor.
# rma still performs Fisher scoring, its convergence check, and likelihood check.
# No app output, tau2= override, or frozen deletion variance is used.
start_tau <- function(y,v) {
 score<-function(t) {w<-1/(v+t); mu<-sum(w*y)/sum(w); sum(w*w*(y-mu)^2)-sum(w)+sum(w*w)/sum(w)}
 if(score(0)<=0) return(0)
 hi<-max(var(y),max(v),1e-8)
 while(score(hi)>0) hi<-hi*2
 uniroot(score,c(0,hi),tol=1e-14,maxiter=1000)$root
}
