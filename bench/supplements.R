# Mappings checked against the installed metadat Rd descriptions/examples.
# These add formats not named yi/vi in the documentation extraction.
add <- function(def, expr) {
 val<-try(eval(expr,list(dat=d)),silent=TRUE)
 if(inherits(val,'try-error')) {errors<<-c(errors,as.character(val));return()}
 capture(val,def,paste(deparse(expr,width.cutoff=500),collapse=' '))
}
if(is.data.frame(d)) {
 nms<-names(d)
 if(all(c('ai','n1i','ci','n2i') %in% nms) && !length(configs))
  add('RR',quote(escalc(measure='RR',ai=ai,n1i=n1i,ci=ci,n2i=n2i,data=dat)))
 if(all(c('Ee','Ne','Ec','Nc') %in% nms))
  add('RR',quote(escalc(measure='RR',ai=Ee,n1i=Ne,ci=Ec,n2i=Nc,data=dat)))
 if(all(c('m1i','sd1i','n1i','m2i','sd2i','n2i') %in% nms) && !length(configs))
  add('MD',quote(escalc(measure='MD',m1i=m1i,sd1i=sd1i,n1i=n1i,m2i=m2i,sd2i=sd2i,n2i=n2i,data=dat)))
 if(all(c('Me','Se','Ne','Mc','Sc','Nc') %in% nms))
  add(if(nm=='dat.furukawa2003') 'SMD' else 'MD', substitute(escalc(measure=M,m1i=Me,sd1i=Se,n1i=Ne,m2i=Mc,sd2i=Sc,n2i=Nc,data=dat),list(M=if(nm=='dat.furukawa2003') 'SMD' else 'MD')))
 if(nm=='dat.bakdash2021') add('ZCOR stored',quote(data.frame(yi=dat$es.z,vi=dat$vi.z)))
 if(nm=='dat.baskerville2012') add('SMD stored',quote(data.frame(yi=dat$smd,vi=dat$se^2)))
 if(nm=='dat.curtin2002') add('MD stored',quote(data.frame(yi=dat$mean,vi=dat$SE^2)))
 if(nm=='dat.greenland1992') add('coefficient stored',quote(data.frame(yi=dat$b,vi=dat$SE^2)))
 if(nm=='dat.steurer2006') add('logHR stored',quote(data.frame(yi=dat$lnHR,vi=dat$selnHR^2)))
 if(nm=='dat.thompson1999') add('logOR stored',quote(data.frame(yi=dat$logOR,vi=dat$varlogOR)))
 if(nm=='dat.craft2003') add('COR',quote(escalc(measure='COR',ri=ri,ni=ni,data=dat)))
 if(nm=='dat.feng2019') add('PLO',quote(escalc(measure='PLO',xi=depr,ni=n,data=dat)))
 if(nm=='dat.hartmannboyce2018') add('RR',quote(escalc(measure='RR',ai=x.nrt,n1i=n.nrt,ci=x.ctrl,n2i=n.ctrl,data=dat)))
 if(nm=='dat.higgins2008') add('RR available case',quote(escalc(measure='RR',ai=resp.halo,bi=fail.halo,ci=resp.plac,di=fail.plac,data=dat)))
 if(nm=='dat.collins1985a') add('OR recurrent bleeding',quote(escalc(measure='OR',ai=b.xti,n1i=nti,ci=b.xci,n2i=nci,data=dat)))
 if(nm=='dat.cannon2006') for(ep in 1:6) add(paste0('OR endpoint',ep),substitute(escalc(measure='OR',ai=dat[[A]],n1i=dat$nt,ci=dat[[C]],n2i=dat$nc),list(A=paste0('ep',ep,'t'),C=paste0('ep',ep,'c'))))
 if(nm=='dat.lloyd2010') for(ep in c('das','haq')) add(paste('MD',ep),substitute(data.frame(yi=dat[[M]],vi=((dat[[U]]-dat[[L]])/(2*qnorm(.975)))^2),list(M=paste0('mean.',ep),U=paste0('upper.',ep),L=paste0('lower.',ep))))
 if(nm=='dat.rivera2025') add('log diagnostic OR',quote(escalc(measure='OR',ai=TP,bi=FP,ci=FN,di=TN,data=dat)))
 # Single-arm logits exercise the intercept-only numerical engine, not network inference.
 arm<-switch(nm,'dat.baker2009'=c('exac','total'),'dat.dogliotti2014'=c('stroke','total'),
  'dat.dong2013'=c('death','randomized'),'dat.gurusamy2011'=c('death','n'),
  'dat.linde2016'=c('resp','n'),'dat.roever2022'=c('events','total'),
  'dat.ursino2021'=c('events','total'),'dat.woods2010'=c('r','N'),
  'dat.tian2009'=c('deaths','n'))
 if(!is.null(arm)) add('PLO arm-level',substitute(escalc(measure='PLO',xi=dat[[X]],ni=dat[[N]]),list(X=arm[1],N=arm[2])))
 if(nm %in% c('dat.franchini2012','dat.stowe2010')) add('MD arms 1-2',quote(escalc(measure='MD',m1i=y1,sd1i=sd1,n1i=n1,m2i=y2,sd2i=sd2,n2i=n2,data=dat)))
 if(nm=='dat.linde2015') add('RR response arms 1-2',quote(escalc(measure='RR',ai=resp1,n1i=n1,ci=resp2,n2i=n2,data=dat)))
}
if(nm=='dat.maire2019') add('Mann-Kendall s1 stored',quote(data.frame(yi=dat$dat$s1,vi=dat$dat$vars1)))
# Remove duplicate raw yi/vi aliases when documented measure attributes identify the same rows.
if(length(configs)>1 && !is.null(configs[['stored yi/vi']])) {
 raw<-configs[['stored yi/vi']]
 if(any(vapply(configs[names(configs)!='stored yi/vi'],function(x)identical(x$yi,raw$yi)&&identical(x$vi,raw$vi),TRUE))) configs[['stored yi/vi']]<-NULL
}
