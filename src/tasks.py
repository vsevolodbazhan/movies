import csv
import os

import luigi

from .genres import Genre
from .movies import get_top_movies


class LoadTopMovies(luigi.Task):
    genre = luigi.EnumParameter(enum=Genre)

    directory_name = luigi.Parameter(default="movie_data")

    @property
    def file_name(self):
        return f"{self.genre.value}_movies.csv"

    def run(self):
        self.output().makedirs()
        movies = get_top_movies(genre=self.genre)

        with self.output().open("w") as output:
            writer = csv.writer(output, delimiter=",")
            for movie in movies:
                writer.writerow(movie.data)

    def output(self):
        return luigi.LocalTarget(os.path.join(self.directory_name, self.file_name))
