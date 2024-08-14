library(tidyverse)
library(janitor)

tuesdata <- tidytuesdayR::tt_load(2024, week = 33)

worlds_fairs <- tuesdata$worlds_fairs

# Countries by continent downloaded from Kaggle
# https://www.kaggle.com/datasets/hserdaraltan/countries-by-continent
countryContinent = read.csv('posts/tt20240813/countriesByContinent.csv') |>
  clean_names()

save(worlds_fairs,countryContinent,file="posts/tt20240813/worldsFairs.Rdata")
