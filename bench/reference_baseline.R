# Small standard-R cross-check, with no BLAS replacement.
text<-readLines('reference.R')
text<-gsub('reference-parts','reference-baseline-parts',text,fixed=TRUE)
text<-gsub('reference-plots.pdf','reference-baseline-plots.pdf',text,fixed=TRUE)
text<-gsub('for(id in names(corpus))','for(id in names(corpus)[vapply(corpus,function(x)length(x$yi)<=5,TRUE)])',text,fixed=TRUE)
text<-text[seq_len(which(grepl('^files<-',text))-1)]
eval(parse(text=text))
cat('NATIVE BASELINE COMPLETE\n')
