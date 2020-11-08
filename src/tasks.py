import os
import luigi
import csv

from .movies import get_top_movies
from .genres import GENRES


class LoadTopMovies(luigi.Task):
    genre = luigi.Parameter()

    directory_name = luigi.Parameter(default="movie_data")

    @property
    def file_name(self):
        return f"{self.genre}_movies.csv"

    def run(self):
        if self.genre not in GENRES:
            raise ValueError(
                "Invalid genre value: {self.genre}. Genre must be one of the following: {GENRES}."
            )

        self.output().makedirs()
        movies = get_top_movies(genre=self.genre)

        with self.output().open("w") as output:
            writer = csv.writer(output, delimiter=",")
            for movie in movies:
                writer.writerow(movie.data)

    def output(self):
        return luigi.LocalTarget(os.path.join(self.directory_name, self.file_name))
