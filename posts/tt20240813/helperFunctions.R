library(tidyverse)
library(ggtext)
library(showtext)
library(janitor)
library(ggdist)
library(ggrepel)
library(scales)
library(gt)
library(paletteer)

col_pal_dis_short = "MetBrewer::Kandinsky"
col_pal_dis_long = "PrettyCols::Autumn"
col_pal_cont = "ggthemes::Blue-Teal"
oneCol = paletteer_d(col_pal_dis_short)[1]
silver = "#e1e1e1"
ltSilver = "#efefef"
gold = "#eecf70"
ltGold = "#f7e8b9"
grn = "#a0e9a7"
ltGrn = "#c4f5c8"

showtext_opts(dpi = 225, regular.wt = 300, bold.wt = 800)

font_add("fa6-brands", 
         "/usr/share/fonts/fontawesome-free-6.6.0-desktop/otfs/Font Awesome 6 Brands-Regular-400.otf")
showtext_auto(enable = TRUE)

theme_set(theme_classic(base_size = 14, base_family = 'sans'))

ttText <- str_glue("**#TidyTuesday** &bull; Sources: Wikipedia and S. Altan Kaggle dataset")
gh <- str_glue("<span style='font-family: \"fa6-brands\"'>&#xf09b;</span>")
li <- str_glue("<span style='font-family:\"fa6-brands\"'>&#xf08c;</span>")
caption_text <- str_glue("{ttText} <br> {gh} datawolf04 {li} wolf-253b6625a")

theme_simple = function(...){
  theme_classic() %+replace%
    
    theme(
      legend.title = element_markdown(size = rel(0.8), hjust = 0.5),
      legend.text = element_text(size = rel(0.7)), 
      
      plot.title.position = 'plot',
      plot.caption.position = 'plot',
      
      strip.background = element_rect(
        fill=paletteer_d(col_pal_dis_short)[4]),
      strip.text = element_text(color = "white"),
      
      plot.margin = margin(t = 20, r = 20, b = 20, l = 20),
      plot.title = element_text(size = rel(1.5),
                                margin = margin(0,0,10,0)),
      axis.title.x = element_text(margin = margin(10, 0, 0, 0), size = rel(1.2)),
      axis.title.y = element_text(margin = margin(0, 10, 0, 0), size = rel(1.2),angle=90),
      axis.text = element_text(size=rel(0.8)),
      plot.caption = element_markdown(
        size        = rel(.7),
        family      = "sans",
        color       = "grey25",
        lineheight  = 0.6,
        hjust       = 0,
        halign      = 0,
        margin      = margin(t = 10, b = 5)
      )
    ) 
}

calcFairLengthMonths = function(startMonth,startYear,endMonth,endYear){
  stopifnot(is.numeric(c(startMonth,startYear,endMonth,endYear)))
  failMsg = str_glue(
    "Fair must start before it ends. \ Start date: {startMonth}/{startYear}. \ End date: {endMonth}/{endYear}. \ \n\n")
  if(startYear > endYear){
    stop(failMsg)
  } else if (startYear == endYear){
    if(startMonth > endMonth){
      stop(failMsg)
    } else {
      fLen = endMonth - startMonth + 1
    }
  } else {
    yrs = endYear - startYear
    fLen = 12*yrs + endMonth - startMonth + 1
  }
  
  return(fLen)
}

calcFLMV <- Vectorize(calcFairLengthMonths)

my_table_formatting = function(df){
  df |>
    tab_source_note(
      source_note = md(ttText)
    ) |>
    tab_style(
      style = list(
        cell_fill(color = paletteer_d(col_pal_dis_short)[1]),
        cell_text(color = 'white')
        ),
      locations=cells_title()
    ) |>
    tab_style(
      style = list(
          cell_fill(color = paletteer_d(col_pal_dis_short)[1]),
          cell_text(color = 'white')
      ),        
      locations=cells_source_notes()
    ) |>
    tab_style(
      style = list(
        cell_fill(color = paletteer_d(col_pal_dis_short)[1]),
        cell_text(color = 'white')
      ),        
      locations=cells_footnotes()
    ) |>
    tab_style(
      style = list(
        cell_fill(color = paletteer_d(col_pal_dis_short)[4]),
        cell_text(color = 'white')
      ),
      locations=cells_column_labels()
    ) 
  }
