library(metafor)
source('cache_refits.R');source('prime_refits_files.R')
text<-readLines('reference.R')
text<-gsub('reference-parts','reference-parallel-parts',text,fixed=TRUE)
text<-gsub('reference-plots.pdf','reference-parallel-plots.pdf',text,fixed=TRUE)
selection<-if('--verify' %in% commandArgs(TRUE)) 'length(x$yi)<=5' else 'length(x$yi)>1000'
text<-gsub('for(id in names(corpus))',paste0('for(id in names(corpus)[vapply(corpus,function(x)',selection,',TRUE)])'),text,fixed=TRUE)
text<-text[seq_len(which(grepl('^files<-',text))-1)]
text<-append(text,'  rm(list=ls(refit_cache,all.names=TRUE),envir=refit_cache)',after=which(grepl('^ c<-corpus',text)))
text<-gsub('  loo<-leave1out','  prime_refits(res,id); loo<-leave1out',text,fixed=TRUE)
text<-gsub("bdl<-baujat(dl)","prime_refits(dl,id); bdl<-baujat(dl)",text,fixed=TRUE)
eval(parse(text=text))
cat('PARALLEL REFERENCE COMPLETE\n')
