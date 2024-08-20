library(tidyverse)
library(ggtext)
library(showtext)
library(janitor)
library(ggdist)
library(ggrepel)
library(scales)
library(gt)
library(paletteer)
library(grid)

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
twoColorPal = colors()[c(644,30)]

showtext_opts(dpi = 225, regular.wt = 300, bold.wt = 800)

font_add("fa6-brands", 
         "/usr/share/fonts/fontawesome-free-6.6.0-desktop/otfs/Font Awesome 6 Brands-Regular-400.otf")
showtext_auto(enable = TRUE)

theme_set(theme_classic(base_size = 14, base_family = 'sans'))

ttStart <- str_glue("**#TidyTuesday** &bull; Sources: Ian Visits and f. hull dataset")
ttText <- str_glue("**#TidyTuesday** &bull; Sources: Ian Visits and f. hull dataset, Wikipedia and royal.uk logos")
gh <- str_glue("<span style='font-family: \"fa6-brands\"'>&#xf09b;</span>")
li <- str_glue("<span style='font-family:\"fa6-brands\"'>&#xf08c;</span>")
caption_text <- str_glue("{ttText} <br> {gh} datawolf04 {li} wolf-253b6625a")

theme_mine = function(...){
  theme_classic() %+replace%
    
    theme(
      legend.title = element_markdown(size = rel(0.8), hjust = 0.5),
      legend.text = element_text(size = rel(0.7)), 
      legend.position = 'bottom',
      legend.background = element_rect(fill='grey85',color=NA),
      
      plot.title.position = 'plot',
      plot.caption.position = 'plot',
      plot.background = element_rect(fill='grey95'),
      
      strip.background = element_rect(
        fill=paletteer_d(col_pal_dis_short)[4]),
      strip.text = element_text(color = "white"),
      
      plot.margin = margin(t = 20, r = 20, b = 20, l = 20),
      plot.title = element_text(size = rel(1.5),
                                margin = margin(0,0,10,0),hjust=0.5),
      plot.subtitle = element_text(size = rel(1.25),
                                margin = margin(0,0,10,0),hjust=0.5),
      axis.title.x = element_text(margin = margin(10, 0, 0, 0), size = rel(1.2)),
      axis.title.y = element_text(margin = margin(0, 10, 0, 0), size = rel(1.2),angle=90),
      axis.text = element_text(size=rel(0.8)),
      plot.caption = element_markdown(
        size        = rel(.7),
        family      = "sans",
        color       = "grey25",
        lineheight  = 0.6,
        hjust       = 1,
        halign      = 0,
        margin      = margin(t = 10, b = 5)
      )
    ) 
}


my_table_formatting = function(df){
  df |>
    tab_source_note(
      source_note = md(ttStart)
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
    ) |>
    tab_style(
      style = list(
        cell_fill(color = paletteer_d(col_pal_dis_short)[4]),
        cell_text(color = 'white')
      ),
      locations=cells_column_spanners()
    ) 
  }


