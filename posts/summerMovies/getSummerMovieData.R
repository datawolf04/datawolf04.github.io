# Load the data
tuesdata <- tidytuesdayR::tt_load('2024-07-30')
summer_movie_genres <- tuesdata$summer_movie_genres
summer_movies <- tuesdata$summer_movies

fName = 'posts/summerMovies/summerMovie.RData'

save(tuesdata, summer_movie_genres, summer_movies, file=fName)