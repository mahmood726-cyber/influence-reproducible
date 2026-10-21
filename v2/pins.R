# Shared fail-closed runtime gate; E3 scripts themselves are retained unmodified.
v2_versions <- function() {
  userlibs <- strsplit(Sys.getenv('R_LIBS_USER'), .Platform$path.sep, fixed=TRUE)[[1]]
  .libPaths(c(userlibs[nzchar(userlibs)], .libPaths()))
  if (as.character(getRversion()) != '4.6.0') stop('V2 requires R 4.6.0; found ', getRversion())
  for (p in c('metafor', 'jsonlite', 'digest')) {
    if (!requireNamespace(p, quietly=TRUE)) stop('Missing installed package: ', p)
    got <- as.character(packageVersion(p))
    cat('V2 package ', p, ' ', got, '\n', sep='')
    if (p == 'metafor' && got != '5.2.1') stop('V2 requires metafor 5.2.1')
    if (p == 'jsonlite' && got != '2.0.0') stop('V2 requires jsonlite 2.0.0')
    if (p == 'digest' && got != '0.6.39') stop('V2 requires digest 0.6.39')
  }
  cat(R.version.string, '\n')
}
