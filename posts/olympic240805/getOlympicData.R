# Load the data
tuesdata <- tidytuesdayR::tt_load(2024, week = 32)

olympics <- tuesdata$olympics |>
  janitor::clean_names()

fName = 'posts/olympic240805/olympicMedalResults.RData'

save(olympics, file=fName)