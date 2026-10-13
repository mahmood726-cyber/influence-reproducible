# Recompute the correctly named Mann-Kendall configuration (same input numbers).
text<-readLines('reference.R')
text<-gsub('reference-parts','reference-accelerated-parts',text,fixed=TRUE)
text<-gsub('reference-plots.pdf','reference-label-plots.pdf',text,fixed=TRUE)
text<-gsub('for(id in names(corpus))','for(id in "dat.maire2019::Mann-Kendall s1 stored")',text,fixed=TRUE)
text<-text[seq_len(which(grepl('^files<-',text))-1)]
eval(parse(text=text))
