# Fast runtime gates and scheduling check; no fits or worker processes launched.
source('v2/pins.R')
v2_versions()
expect_error <- function(f) {
  caught <- FALSE
  tryCatch(f(),error=function(e) {cat('Expected rejection: ',conditionMessage(e),'\n',sep='');caught<<-TRUE})
  stopifnot(caught)
}
getRversion <- function() numeric_version('4.5.1')
expect_error(v2_versions)
rm(getRversion)
packageVersion <- function(pkg) if(pkg=='metafor') numeric_version('5.0.1') else utils::packageVersion(pkg)
expect_error(v2_versions)
rm(packageVersion)
cat('R/PACKAGE VERSION CONTROLS 2/2 rejected\n')
expressions <- parse('validate.R')
# Load just the definitions through environment(main), before any execution.
for (expression in expressions) {
  if (identical(expression,quote(status <- 0L))) break
  eval(expression,.GlobalEnv)
}
environment(main)$source('bench/prime_validation.R')
stopifnot(identical(body(prime_validation)[[3]],quote(workers <- 1L)))
cat('R PROCESS CAP 1/1 parent plus one worker\n')
