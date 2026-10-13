# Independent reference worker, disjoint output directory; same reference.R code.
text <- readLines('reference.R')
text <- gsub("reference-parts", "reference-fast-parts", text, fixed=TRUE)
text <- gsub("reference-plots.pdf", "reference-fast-plots.pdf", text, fixed=TRUE)
text <- gsub("for(id in names(corpus))", "for(id in names(corpus)[vapply(corpus, function(x) length(x$yi) < 500, TRUE)])", text, fixed=TRUE)
text <- text[seq_len(which(grepl('^files<-',text))-1)]
eval(parse(text=text))
cat('SMALL REFERENCE WORKER COMPLETE\n')
