library(metafor)
source('json.R')
c<-readRDS('corpus.rds');out<-list()
pdf('radial-reference-plots.pdf')
for(id in names(c)) {
 d<-c[[id]];f<-rma(d$yi,d$vi,method='FE',test='z');points<-radial(f)
 out[[id]]<-list(x=points$x,z=points$y,slope=as.numeric(coef(f)),resid=points$y-as.numeric(coef(f))*points$x)
}
dev.off();write_json(out,'radial-reference.json')
cat('RADIAL REFERENCE',length(out),'configurations\n')
