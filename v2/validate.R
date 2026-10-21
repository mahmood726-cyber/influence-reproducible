v2_main <- function() {
  source('v2/pins.R')
  v2_versions()
  # Export the parent's selected order so each unmodified E3 subprocess uses it.
  Sys.setenv(R_LIBS=paste(.libPaths(),collapse=.Platform$path.sep))
  python <- Sys.which('python')
  if (!nzchar(python)) python <- Sys.which('py')
  if (!nzchar(python)) stop('V2 requires Python 3.13 or later (standard library only)')
  rscript <- file.path(R.home('bin'), if (.Platform$OS.type=='windows') 'Rscript.exe' else 'Rscript')
  status <- system2(python, c('-u', shQuote('v2/tools/validate.py'), shQuote(rscript)))
  if (status != 0L) stop('V2 checks failed; see outputs/v2/')
  0L
}
