library(tidyverse)
library(janitor)

tuesdata <- tidytuesdayR::tt_load('2024-08-20')
## OR
tuesdata <- tidytuesdayR::tt_load(2024, week = 34)

monarchDat <- tuesdata$english_monarchs_marriages_df |>
  clean_names()

save(monarchDat,file='posts/tt20240819/englishMonarchy.RData')