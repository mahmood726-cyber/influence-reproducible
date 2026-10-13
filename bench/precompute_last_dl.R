library(metafor)
source('cache_refits.R');source('prime_refits_files.R')
corpus<-readRDS('corpus.rds')
id<-'dat.moura2021::ZCOR';stopifnot(id %in% names(corpus))
c<-corpus[[id]]
res<-rma(c$yi,c$vi,method='DL',test='z')
prime_refits(res,id,worker_limit=1)
cat('LAST DATASET DL PRECOMPUTATION COMPLETE\n')
