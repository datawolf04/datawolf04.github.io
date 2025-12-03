library(tidyverse)

tuesdata <- tidytuesdayR::tt_load('2025-12-02')
explSnow <- tuesdata$sechselaeuten

save(explSnow,file="explSnow.RData")

