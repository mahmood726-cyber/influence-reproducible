# Fresh, file-based workers following prime_refits_files.R/refit_worker.R.
# No historical checkpoint can enter this unique per-call directory.
prime_validation <- function(model) {
  if(length(model$yi)<500L)return(invisible(NULL))
  workers<-3L
  d<-list(yi=as.numeric(model$yi),vi=as.numeric(model$vi),method=model$method,test=model$test,level=model$level,control=model$control)
  dir.create('.validate-work',showWarnings=FALSE)
  folder<-tempfile('fresh-refits-',tmpdir='.validate-work');dir.create(folder)
  folder<-normalizePath(folder,winslash='/');root<-normalizePath('.',winslash='/')
  saveRDS(d,file.path(folder,'input.rds'))
  script<-normalizePath('bench/validation_worker.R',winslash='/')
  rscript<-file.path(R.home('bin'),if(.Platform$OS.type=='windows')'Rscript.exe' else 'Rscript')
  previous<-Sys.getenv('OPENBLAS_NUM_THREADS',unset=NA_character_)
  Sys.setenv(OPENBLAS_NUM_THREADS='1')
  on.exit(if(is.na(previous))Sys.unsetenv('OPENBLAS_NUM_THREADS') else Sys.setenv(OPENBLAS_NUM_THREADS=previous),add=TRUE)
  complete<-FALSE
  on.exit({if(!complete)for(f in list.files(folder,pattern='[.]pid$',full.names=TRUE)) {
    pid<-suppressWarnings(as.integer(readLines(f,warn=FALSE)))
    if(length(pid)==1L&&!is.na(pid))try(tools::pskill(pid),silent=TRUE)
  }},add=TRUE)
  for(i in seq_len(workers)) {
    status<-file.path(folder,paste0(i,'.status'));log<-file.path(folder,paste0(i,'.log'))
    args<-c('--vanilla',shQuote(script),shQuote(root),shQuote(folder),i,workers,shQuote(status))
    if(system2(rscript,args,stdout=log,stderr=log,wait=FALSE)!=0)stop('Could not start fresh R worker')
  }
  start<-proc.time()[['elapsed']];last<- -1L
  repeat {
    chunks<-list.files(folder,pattern='^chunk-[0-9]+[.]rds$',full.names=TRUE)
    if(length(chunks)!=last) {
      done<-sum(vapply(chunks,function(f)length(readRDS(f)$values),1L))
      cat('FRESH REFITS ',done,'/',length(d$yi),' in ',workers,' local workers\n',sep='');flush.console();last<-length(chunks)
    }
    statuses<-file.path(folder,paste0(seq_len(workers),'.status'))
    existing<-statuses[file.exists(statuses)]
    if(length(existing)&&any(vapply(existing,function(f)readLines(f,warn=FALSE)[1]!='0',TRUE)))stop('Fresh refit worker failed; see ',folder)
    if(length(existing)==workers)break
    if(proc.time()[['elapsed']]-start>21600)stop('Fresh refit workers exceeded six-hour bound; see ',folder)
    Sys.sleep(1)
  }
  complete<-TRUE
  assign('.yi',d$yi,refit_cache);assign('.vi',d$vi,refit_cache)
  ids<-integer()
  for(f in list.files(folder,pattern='^chunk-[0-9]+[.]rds$',full.names=TRUE)) {
    chunk<-readRDS(f);stopifnot(identical(chunk$input,d))
    for(v in chunk$values) {
      ids<-c(ids,v$i)
      key<-paste(as.integer(serialize(list(omitted=as.integer(v$i),method=d$method,test=d$test,level=d$level,control=v$control),NULL)),collapse=',')
      assign(key,v$value,refit_cache)
    }
  }
  stopifnot(length(ids)==length(d$yi),!anyDuplicated(ids),setequal(ids,seq_along(d$yi)))
  cat('FRESH REFITS COMPLETE ',length(ids),'/',length(d$yi),'\n',sep='');flush.console()
}
