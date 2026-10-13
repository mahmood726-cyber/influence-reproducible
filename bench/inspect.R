library(metafor)
library(metadat)
cat(R.version.string, '\n', as.character(packageVersion('metafor')), '\n')
writeLines(capture.output(getS3method('influence','rma.uni')), 'influence-r-source.txt')
writeLines(capture.output(getS3method('baujat','rma')), 'baujat-r-source.txt')
ds <- data(package='metadat')$results
write.csv(ds, 'dataset-inventory.csv', row.names=FALSE)
rd <- tools::Rd_db('metadat')
dir.create('documentation', showWarnings=FALSE)
for(n in names(rd)) {
 txt <- capture.output(tools::Rd2ex(rd[[n]]))
 writeLines(txt, file.path('documentation', sub('Rd$','R', n)))
 writeLines(capture.output(tools::Rd2txt(rd[[n]])),file.path('documentation',sub('Rd$','txt',n)))
}
cat('datasets:',nrow(ds),'\n')

