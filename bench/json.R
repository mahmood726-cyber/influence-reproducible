json <- function(x) {
 if(is.null(x)) return('null')
 if(is.data.frame(x)) x<-as.list(x)
 if(is.list(x)) {
  vals<-vapply(x,json,'')
  if(!is.null(names(x))) return(paste0('{',paste(paste0(vapply(names(x),json,''),':',vals),collapse=','),'}'))
  return(paste0('[',paste(vals,collapse=','),']'))
 }
 if(length(x)!=1) return(paste0('[',paste(vapply(as.list(x),json,''),collapse=','),']'))
 if(is.na(x) || (is.numeric(x) && !is.finite(x))) return('null')
 if(is.logical(x)) return(if(x)'true' else 'false')
 if(is.numeric(x)) return(sprintf('%.17g',x))
 encodeString(as.character(x),quote='"',na.encode=FALSE)
}
write_json <- function(x,path) writeLines(json(x),path,useBytes=TRUE)
