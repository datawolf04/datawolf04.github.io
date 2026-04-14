library(tidyverse)

tuesdata <- tidytuesdayR::tt_load('2026-04-14')
## OR
tuesdata <- tidytuesdayR::tt_load(2026, week = 15)

beaufort_scale <- tuesdata$beaufort_scale
birds <- tuesdata$birds
sea_states <- tuesdata$sea_states
ships <- tuesdata$ships

## Merge ship/weather data
ships <- left_join(ships,sea_states,by='sea_state_class') |> 
  left_join(beaufort_scale,by='wind_speed_class')


save(birds, ships, file='Tongarewa.RData')