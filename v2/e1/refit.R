# E1 exclusion re-fits under the archive REML policy. Usage: Rscript refit.R corpus.json sets.json out.jsonl
source("v2/pins.R")
v2_versions()
suppressMessages({library(metafor); library(jsonlite)})
a <- commandArgs(TRUE)
source("v2/e1/starts.R")
corpus <- fromJSON(a[1], simplifyVector = TRUE); sets <- fromJSON(a[2], simplifyVector = FALSE)
out <- a[3]
env <- list(R = R.version.string, metafor = as.character(packageVersion("metafor")), jsonlite = as.character(packageVersion("jsonlite")))
cat(toJSON(list(env = env), auto_unbox = TRUE, digits = NA), "\n", file = out, append = FALSE)
done <- character()
fit <- function(tag, id, excl) {
  c <- corpus[[id]]; keep <- setdiff(seq_along(c$yi), excl + 1)
  y <- c$yi[keep]; v <- c$vi[keep]
  ctl <- list(threshold = 1e-12, maxiter = 10000, stepadj = 1)
  ctl$tau2.init <- start_tau(y, v); ctl$threshold <- 1e-12 * max(1, ctl$tau2.init)
  warns <- character()
  t0 <- Sys.time()
  r <- tryCatch(withCallingHandlers({
    res <- rma(y, v, method = "REML", test = "z", control = ctl)
    list(k = res$k, mu = as.numeric(coef(res)), se = res$se, zval = res$zval, pval = res$pval, ci.lb = res$ci.lb,
         ci.ub = res$ci.ub, tau2 = res$tau2, I2 = res$I2, H2 = res$H2, QE = res$QE, QEp = res$QEp)
  }, warning = function(w) { warns <<- c(warns, conditionMessage(w)); invokeRestart("muffleWarning") }),
  error = function(e) list(error = conditionMessage(e)))
  r$tag <- tag; r$id <- id; r$exclude <- excl; r$warnings <- warns; r$sec <- as.numeric(Sys.time() - t0, units = "secs")
  cat(toJSON(r, auto_unbox = TRUE, digits = NA), "\n", file = out, append = TRUE, sep = "")
}
for (id in names(sets$F)) { s <- sets$F[[id]]; if (!isTRUE(s$refused)) fit("F", id, unlist(s$exclude)) }
for (s in sets$R) fit(paste0("R", s$rep), s$id, unlist(s$exclude))
cat("{\"done\":true}\n", file = out, append = TRUE)
