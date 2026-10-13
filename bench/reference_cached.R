# Compute large configurations with exact repeated-fit reuse.
library(metafor)
source('cache_refits.R')
text<-readLines('reference.R')
text<-gsub('reference-parts','reference-cached-parts',text,fixed=TRUE)
if('--verify2' %in% commandArgs(TRUE)) text<-gsub('reference-cached-parts','reference-cache-check-parts',text,fixed=TRUE)
text<-gsub('reference-plots.pdf','reference-cached-plots.pdf',text,fixed=TRUE)
selection<-if('--verify2' %in% commandArgs(TRUE)) 'length(x$yi) <= 5' else if('--verify' %in% commandArgs(TRUE)) 'length(x$yi) <= 25' else 'length(x$yi) >= 678'
if('--medium' %in% commandArgs(TRUE)) selection<-'length(x$yi)>=678 && length(x$yi)<=1000'
replacement<-paste0('for(id in names(corpus)[order(vapply(corpus,function(x)length(x$yi),1L))][vapply(corpus[order(vapply(corpus,function(x)length(x$yi),1L))],function(x)',selection,',TRUE)])')
text<-gsub('for(id in names(corpus))',replacement,text,fixed=TRUE)
text<-text[seq_len(which(grepl('^files<-',text))-1)]
text<-append(text,'  rm(list=ls(refit_cache,all.names=TRUE),envir=refit_cache)',after=which(grepl('^ c<-corpus',text)))
eval(parse(text=text))
cat('CACHED REFERENCE COMPLETE\n')
