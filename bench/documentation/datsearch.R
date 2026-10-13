### Name: datsearch
### Title: Search Function for the Datasets
### Aliases: datsearch
### Keywords: file

### ** Examples

# note: the examples below are not run since they require interactivity

if (FALSE) {

   # start the function in the interactive mode
   datsearch()

   # find all datasets tagged with the concept term 'standardized mean differences'
   datsearch("standardized mean differences")

   # find all datasets tagged with the concept terms 'odds ratio' and 'multilevel'
   datsearch("odds ratio, multilevel")

   # do a full-text search for the term 'infarct'
   datsearch("infarct", concept=FALSE)

   # do a full-text search for 'rma.mv(' (essentially finds all datasets where
   # the rma.mv() function was used in the examples section of a help file)
   datsearch("rma.mv(", concept=FALSE)

}



