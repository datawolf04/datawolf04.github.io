tuesdata <- tidytuesdayR::tt_load(2024, week = 36)

qname_levels_single_response_crosswalk <- tuesdata$qname_levels_single_response_crosswalk
stackoverflow_survey_questions <- tuesdata$stackoverflow_survey_questions
stackoverflow_survey_single_response <- tuesdata$stackoverflow_survey_single_response

source('posts/tt20240903/helperFunctions.R')

save(qname_levels_single_response_crosswalk, stackoverflow_survey_questions, 
     stackoverflow_survey_single_response,file = 'posts/tt20240903/soSurvey.RData')