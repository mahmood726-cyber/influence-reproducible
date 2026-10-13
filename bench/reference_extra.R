# One appended IPD configuration; existing numeric checkpoint indexes are stable.
text<-readLines('reference.R')
text<-gsub('reference-parts','reference-accelerated-parts',text,fixed=TRUE)
text<-gsub('reference-plots.pdf','reference-extra-plots.pdf',text,fixed=TRUE)
text<-gsub('for(id in names(corpus))','for(id in "dat.huber2000::MD recurrence IPD")',text,fixed=TRUE)
text<-text[seq_len(which(grepl('^files<-',text))-1)]
eval(parse(text=text))
