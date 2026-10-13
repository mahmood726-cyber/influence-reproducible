library(metafor)
library(metadat)
source('json.R')
inventory <- data(package='metadat')$results
corpus <- list(); audit <- list(); extraction <- list()
for (nm in inventory[,'Item']) {
  e <- new.env(parent=globalenv()); data(list=nm, package='metadat', envir=e)
  configs <- list(); errors <- character()
  capture <- function(d, definition, source) {
    if (!is.data.frame(d) || !all(c('yi','vi') %in% names(d))) return()
    if (!is.numeric(d$yi) || !is.numeric(d$vi)) return()
    ok <- is.finite(d$yi) & is.finite(d$vi) & d$vi > 0
    if (sum(ok)<3) return()
    key <- definition
    if (is.null(configs[[key]]) || sum(ok)>length(configs[[key]]$yi))
      configs[[key]] <<- list(dataset=nm, definition=definition, source=source,
       yi=unname(d$yi[ok]), vi=unname(d$vi[ok]), rows=which(ok), omitted=which(!ok))
  }
  d <- get(nm,e)
  capture(d,'stored yi/vi',paste0(nm,'$yi / ',nm,'$vi'))
  f <- file.path('documentation',paste0(nm,'.R'))
  ex <- if(file.exists(f)) try(parse(text=sub('^##D ?', '',readLines(f))),silent=TRUE) else expression()
  if (!inherits(ex,'try-error')) for (expr in ex) {
    txt <- paste(deparse(expr,width.cutoff=500),collapse=' ')
    # Evaluate documented preparation only. Fit calls with measure= are escalc recipes.
    if (grepl('rma(\\.uni)?\\(',txt) && grepl('measure\\s*=',txt)) {
      call <- if(is.call(expr) && as.character(expr[[1]])[1] %in% c('<-','=')) expr[[3]] else expr
      if(is.call(call) && as.character(call[[1]])[1] %in% c('rma','rma.uni')) {
        call[[1]] <- as.name('escalc')
        call <- call[!names(call) %in% c('mods','method','test','slab','random','struct','control')]
        expr <- call; txt <- paste(deparse(expr,width.cutoff=500),collapse=' ')
      }
    }
    if (!is.call(expr)) next
    head <- as.character(expr[[1]])[1]
    if (!(head %in% c('<-','=','escalc','data'))) next
    if(grepl('\\brma[.(]|\\blm\\(|lmer|read\\.|download|source\\(|install|options\\(|par\\(|settings.meta|metagen|metabin|metacont|pairwise\\(',txt)) next
    val <- try(withCallingHandlers(eval(expr,e),warning=function(w){errors <<- c(errors,conditionMessage(w));invokeRestart('muffleWarning')}),silent=TRUE)
    if(inherits(val,'try-error')) {errors<-c(errors,paste(txt,as.character(val)));next}
    if(grepl('escalc\\(',txt)) {
      def <- if(is.data.frame(val)) attr(val$yi,'measure') else NULL
      if(is.null(def)) def<-txt
      capture(val,def,txt)
    }
    for(obj in ls(e)) {
      val2<-get(obj,e)
      if(is.data.frame(val2)) {
        def<-attr(val2$yi,'measure'); if(is.null(def)) def<-'stored yi/vi'
        capture(val2,def,txt)
      }
    }
  }
  source('supplements.R',local=TRUE)
  if(length(configs)) for(key in names(configs)) {
    id<-paste(nm,key,sep='::'); corpus[[id]]<-configs[[key]]
  }
  audit[[nm]]<-list(status=if(length(configs)) 'used' else 'excluded', configurations=names(configs),
    reason=if(length(configs)) 'documented numeric yi/vi or escalc; finite yi and positive finite vi; k >= 3' else paste('No extracted applicable pair; columns:',paste(names(d),collapse=', ')), errors=errors)
}
# IPD also has sufficient ingredients for a documented escalc MD calculation.
# Keep this configuration last so checkpoint indexes of earlier configurations remain stable.
d<-metadat::dat.huber2000
ids<-unique(d$study)
summ<-do.call(rbind,lapply(ids,function(id){
 tr<-d$recurrences[d$study==id & d$treatment=='Uro-Vaxom']
 co<-d$recurrences[d$study==id & d$treatment=='Placebo']
 data.frame(study=as.character(id),m1i=mean(tr),sd1i=sd(tr),n1i=length(tr),m2i=mean(co),sd2i=sd(co),n2i=length(co))
}))
md<-escalc(measure='MD',m1i=m1i,sd1i=sd1i,n1i=n1i,m2i=m2i,sd2i=sd2i,n2i=n2i,data=summ)
stopifnot(all(is.finite(md$yi)),all(md$vi>0),nrow(md)>=3)
corpus[['dat.huber2000::MD recurrence IPD']]<-list(dataset='dat.huber2000',definition='MD recurrence IPD',source='Group participant recurrences by study and treatment (Uro-Vaxom minus Placebo), compute sample means, SDs, n; escalc MD',yi=unname(md$yi),vi=unname(md$vi),rows=seq_len(nrow(md)),omitted=integer(),source_studies=summ$study)
audit[['dat.huber2000']]<-list(status='used',configurations='MD recurrence IPD',reason='IPD recurrence counts summarized per study and arm for escalc MD; numerical benchmark, not the WMW analysis in the package example')
audit[['dat.metap']]$reason<-'P-value-only examples; no study effect estimates with sampling variances or documented escalc ingredients'
write_json(corpus,'corpus.json'); saveRDS(corpus,'corpus.rds'); write_json(audit,'corpus-audit.json')
cat(length(corpus),'configurations from',sum(vapply(audit,function(x)x$status=='used',TRUE)),'datasets\n')
print(sort(sapply(corpus,function(x)length(x$yi)),decreasing=TRUE)[1:15])
