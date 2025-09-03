library(tidyverse)
library(gt)
library(gtExtras)
library(readxl)
library(grid)
library(gtable)
library(ggtext)
library(showtext)
library(janitor)
library(ggdist)
library(ggrepel)
library(scales)
library(paletteer)

showtext_opts(dpi = 225, regular.wt = 300, bold.wt = 800)

font_add("fa7-brands", 
         "/usr/share/fonts/fontawesome-free-7.0.1-desktop/otfs/Font Awesome 7 Brands-Regular-400.otf")
showtext_auto(enable = TRUE)

srcTxt <- str_glue("Source: nc.milesplit.com")
gh <- str_glue("<span style='font-family: \"fa7-brands\"'>&#xf09b;</span>")
li <- str_glue("<span style='font-family:\"fa7-brands\"'>&#xf08c;</span>")
caption_text <- str_glue("{srcTxt} <br> {gh} datawolf04 {li} wolf-253b6625a")

ghLogo = html(web_image('github.png',height = 15))
liLogo = html(web_image('linkedin.png',height = 15))
tabCaption <- str_glue("{srcTxt} <br> {ghLogo} datawolf04 {liLogo} wolf-253b6625a")

gt_cc_table <- function(tbl_dat) {
  tbl_dat |> gt() |> 
    tab_options(
      quarto.use_bootstrap = TRUE, # Enable Bootstrap classes
      heading.background.color = 'darkgrey',
      column_labels.background.color = 'darkgrey',
      table.font.color = '#004d66'
    ) |> 
    tab_style(
      style = cell_fill(color = "skyblue", alpha=0.25), # Choose your desired color
      locations = cells_body(rows = seq(1, nrow(tbl_dat), 2))
    )
}
  
getFileName <-function(gender){
  fName <- ifelse(gender == "Boys", "../../resources/meetResultsBoys2025.xlsx", 
      ifelse(gender == "Girls", "../../resources/meetResultsGirls2025.xlsx", NA))
  return(fName)
} 

getSheetName <- function(meetID,gender,level){
  sheetName <- paste0(meetID,gender,level)
  return(sheetName)
}

getScoringTeams <- function(results,minScoring=5){
  scoringTeams <- results |> group_by(Team) |> summarize(count = n()) |> 
    filter(count >= minScoring) |> select(Team) |> deframe()
  return(scoringTeams)
}

getIncompleteTeams <- function(results,minScoring=5){
  incTeams <- results |> group_by(Team) |> summarize(count = n()) |> 
    filter(count < minScoring) |> select(Team) |> deframe()
  return(incTeams)
}

getVarsityRunners <- function(results, nVarsity = 7){
  teamSummary <- results |> group_by(Team) |> summarize(count = n())  
  team1 <- teamSummary$Team[1]
  count1 <- teamSummary$count[1]
  team1Res <- results |> filter(Team == team1) |> arrange(Time)
  if(count1 > nVarsity){
    team1Res = team1Res[1:nVarsity, ]
  }
  varsityResults <- team1Res

  for(i in 2:nrow(teamSummary)){
    thisTeam <- teamSummary$Team[i]
    thisCount <- teamSummary$count[i]
    thisTeamRes <- results |> filter(Team == thisTeam) |> arrange(Time)
    if(thisCount > nVarsity){
      thisTeamRes <- thisTeamRes[1:nVarsity, ]
    }
    varsityResults <- bind_rows(list(varsityResults, thisTeamRes))
  }

  varsityResults <- varsityResults |> arrange(Time) |> 
    mutate(Place = row_number())
  return(varsityResults)
}

getScorers <- function(results, minScoring = 5, maxScoring = 7){
  scoringTeams = getScoringTeams(results,minScoring = minScoring)
  scorers <- results |> filter(Team %in% scoringTeams) |> 
    getVarsityRunners(nVarsity = maxScoring) |> 
    mutate(Place = row_number())
  return(scorers)
}

calcTeamScore <- function(places,count=5){
    sco = sum(places[1:count])
    return(sco)
}

buildTeamResults <- function(results){
  teamResults <- getScorers(results) |> group_by(Team) |> 
      summarise(Score = calcTeamScore(Place)) |> 
      arrange(Score)
  inc <- getIncompleteTeams(results)
  teamOrder = c(paste0(teamResults$Team," (",teamResults$Score,")"),paste(inc, "(DNS)"))
  teamScores = c(teamResults$Score, rep(NA,length(inc)))
  allTeams = c(teamResults$Team, inc)

  prettyRes = tibble('Team'=allTeams, 'Label'=teamOrder, 'Score'=teamScores) |> 
      mutate(
          Score = ifelse(is.na(Score),"DNS",Score)
      ) 
  return(prettyRes)
}

scoreMeet <- function(results, meetID, meetGender, meetLevel,nScore = 5, nVarsity = 7){
  teams <- getScoringTeams(results)
  meetTitle <- meetID |> str_replace_all('-', ' ') |> str_to_title() |> str_replace(" Xc ", " XC ")
  tableTitle = paste(meetTitle, meetGender, meetLevel)
  teamScore <- numeric(length(teams))
  placements <- character(length(teams))
  scorers <- results |> getScorers(minScoring = nScore, maxScoring = nVarsity)

  for(i in seq_along(teams)){
    tm <- teams[i]
    teamPlaces <- scorers |> filter(Team == tm) |> select(Place) |> deframe()
    placements[i] <- paste(teamPlaces, collapse= ", ")
    scoredPlaces <- scorers |> filter(Team == tm) |> select(Place) |> deframe()

    teamScore[i] <- ifelse(length(teamPlaces) >= 5, calcTeamScore(scoredPlaces),
      ifelse(length(teamPlaces) > 0,"DNS", "NONE"))
  }
  teamResults <- data.frame(teams, placements, teamScore) |> arrange(teamScore) |> 
    gt_cc_table() |>
    tab_header(title = tableTitle) |> 
    cols_label(
      teams = "Teams",
      placements = "Athlete Placements",
      teamScore = "Team Score"
    ) |> tab_caption(html(tabCaption))
  return(teamResults)
}

makePlacePlot <- function(results, meetID, meetGender, meetLevel){
  meetTitle <- meetID |> str_replace_all('-', ' ') |> str_to_title() |> str_replace(" Xc ", " XC ")
  pltTitle = paste(meetTitle, meetGender, meetLevel)
  teamRes = buildTeamResults(results = results) |> select(Team, Label)
  results <- results |> left_join(teamRes, by='Team') |> 
    mutate(Team = Label) |> select(-Label) 
  results <- results |> 
    mutate(
      Team = factor(results$Team, levels = teamRes$Label),
      Place = as.integer(Place)
    )

  ggplot(results, aes(x=Place,y=Team,color=Team)) + 
    geom_point(size=2) + guides(color = "none") + 
    labs(caption = caption_text) +
    scale_y_discrete(limits=rev) + 
    theme(axis.title.y = element_blank()) +
    ggtitle(pltTitle) + xlab("Place in race") + theme_minimal() +
    theme(
      plot.caption = element_markdown(size = rel(0.7))
    )
}


makeTimePlot <- function(results, meetID, meetGender, meetLevel){
  meetTitle <- meetID |> str_replace_all('-', ' ') |> str_to_title() |> str_replace(" Xc ", " XC ")
  pltTitle = paste(meetTitle, meetGender, meetLevel)
  pltTitle = paste(pltTitle, "Team times")
  teamRes = buildTeamResults(results = results) |> select(Team, Label)
  results <- results |> left_join(teamRes, by='Team') |> 
    mutate(Team = Label) |> select(-Label) 
  results <- results |> 
    mutate(Team = factor(results$Team, levels = teamRes$Label))

  p1 <- ggplot(results, aes(x=Time,y=Team,color=Team)) + 
    geom_point(size = 2) + guides(color = "none") + 
    theme_minimal() +
    scale_y_discrete(
      limits=rev
    ) +
    labs(
      title = pltTitle,
      subtitle = "Varsity times by team",
      x = "",
      y = ""
    ) + 
    theme( plot.title.position = "plot", plot.subtitle = element_text(hjust = 0.5) ) +
    scale_x_time(labels = \(x) format(as_datetime(x, tz = "UTC"), "%M:%S"))

  medTime = median(results$Time)
  maxDensity = max(density(results$Time)$y)
  medTimeStr = format(as_datetime(medTime, tz = "UTC"), "%M:%OS2")
  p2 <- ggplot(results, aes(x=Time)) + geom_density(fill = "skyblue", alpha = 0.25) +
    geom_vline(xintercept=medTime, linetype = "dashed", color='blue',linewidth=0.5) +
    scale_y_continuous(labels=NULL) + theme_minimal() +
    theme( 
      plot.title.position = "plot", 
      plot.subtitle = element_text(hjust = 0.2),
      panel.grid.major.y = element_blank(),
      panel.grid.minor.y = element_blank(),
      plot.caption = element_markdown(size = rel(0.7))
    ) +
    labs(
      y="",
      subtitle = "Time distribution for all varsity athletes", 
      caption = caption_text
    ) +
    annotate("text", x = medTime+60, y = maxDensity*0.9, hjust = 0,
      label = paste("Median:",medTimeStr), color = 'blue', size= 3) +
    scale_x_time(labels = \(x) format(as_datetime(x, tz = "UTC"), "%M:%S")) 
  
  g1 <- ggplotGrob(p1)
  g2 <- ggplotGrob(p2)
  g <- rbind(g1, g2, size = "first")
  panel_rows <- unique(g$layout[g$layout$name == "panel", "t"])
  g$heights[panel_rows] <- unit(c(5, 1), "null")
  grid.newpage()
  
  return(grid.draw(g))
}

buildTeamTable <- function(results, thisTeam, maxAth = 7){
  rawTab <- results |> filter(Team==thisTeam) |> 
    select(Athlete, Mark) 

  if(nrow(rawTab) < maxAth){
    nAdd <- maxAth - nrow(rawTab)
    for(i in 1:nAdd){
      rawTab <- rawTab |> add_row(Athlete = NA, Mark = NA)
    }
  } else {
    rawTab <- rawTab[1:maxAth, ]
  }

  dashrows <- function(x){
    if(x>7){
      r = c(5,7)
    } else {
      r = 5
    }
    return(r)
  }

  teamTab <- rawTab |> rename(time = Mark) |> gt_cc_table() |> 
    cols_label(Athlete = "Athlete", time = "Time") |> 
    sub_missing(columns = everything(), missing_text = "") |> 
    cols_align(align='center', columns='time') |> 
    tab_style(
        style = cell_borders(
          sides = "bottom",
          color = "grey",
          weight = px(2),
          style = "dashed"
        ),
        locations = cells_body(rows = dashrows(maxAth))
    ) 
  return(teamTab)
}

