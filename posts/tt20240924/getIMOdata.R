tuesdata <- tidytuesdayR::tt_load(2024, week = 39)

country_results_df <- tuesdata$country_results_df
individual_results_df <- tuesdata$individual_results_df
timeline_df <- tuesdata$timeline_df

save(country_results_df,individual_results_df,timeline_df,file='posts/tt20240924/imoData.RData')
