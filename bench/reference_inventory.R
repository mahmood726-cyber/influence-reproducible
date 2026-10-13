library(metafor)
source('json.R')
write_json(as.data.frame(data(package='metafor')$results),'metafor-dataset-inventory.json')
writeLines(capture.output(getS3method('radial','rma')),'radial-r-source.txt')
