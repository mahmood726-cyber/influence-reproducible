# Same R package algorithms with a workspace-local optimized BLAS.
text<-readLines('reference.R')
text<-gsub('reference-parts','reference-accelerated-parts',text,fixed=TRUE)
text<-gsub('reference-plots.pdf','reference-accelerated-plots.pdf',text,fixed=TRUE)
text<-gsub('for(id in names(corpus))','for(id in names(corpus)[order(vapply(corpus,function(x)length(x$yi),1L))])',text,fixed=TRUE)
if('--small' %in% commandArgs(TRUE)) {
 text<-gsub('for(id in names(corpus)[order(vapply(corpus,function(x)length(x$yi),1L))])','for(id in names(corpus)[vapply(corpus,function(x)length(x$yi)<678,TRUE)])',text,fixed=TRUE)
 text<-text[seq_len(which(grepl('^files<-',text))-1)]
}
eval(parse(text=text))
