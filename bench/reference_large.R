# Independent worker for the two largest configurations, separate artifacts.
text <- readLines('reference.R')
text <- gsub('reference-parts','reference-large-parts',text,fixed=TRUE)
text <- gsub('reference-plots.pdf','reference-large-plots.pdf',text,fixed=TRUE)
text <- gsub('for(id in names(corpus))','for(id in names(corpus)[vapply(corpus, function(x) length(x$yi) > 1000, TRUE)])',text,fixed=TRUE)
text <- text[seq_len(which(grepl('^files<-',text))-1)]
eval(parse(text=text))
cat('LARGE REFERENCE WORKER COMPLETE\n')
