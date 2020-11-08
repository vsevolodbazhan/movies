import csv
import os

import luigi
import pandas as pd
from luigi.contrib.sqla import CopyToTable
from luigi.util import requires
from sqlalchemy import Float, Integer, String

from .genres import Genre
from .movies import get_top_movies


class LoadTopMovies(luigi.Task):
    """Download top-50 movies by `genre` and store them in .csv file."""

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
            writer.writerow(movies[0].fields)
            for movie in movies:
                writer.writerow(movie.data)

    def output(self):
        return luigi.LocalTarget(os.path.join(self.directory_name, self.file_name))


@requires(LoadTopMovies)
class CopyMoviesToSQLite(CopyToTable):
    """"Download top-50 movies by `genre` and load them into SQLite."""

    database_name = luigi.Parameter(default="top_movies")

    columns = [
        (["id", Integer()], {"primary_key": True, "autoincrement": True}),
        (["title", String()], {}),
        (["genre", String()], {}),
        (["rating", Float()], {}),
        (["year", Integer()], {}),
        (["runtime", Integer()], {}),
        (["votes", Integer()], {}),
        (["metascore", Integer()], {}),
        (["certificate", String()], {}),
        (["gross", Float()], {}),
    ]

    @property
    def connection_string(self):
        return f"sqlite:///{self.database_name}.db"

    @property
    def table(self):
        genre = self.genre.value.capitalize().replace("-", "")
        return f"Top{genre}Movies"

    def rows(self):
        with self.input().open("r") as input:
            df = pd.read_csv(input)
            splitted = df.to_dict(orient="split")

            # List of `None` values is used
            # to skip `id` field when insertings values
            # into a database table.
            # That allows to generate IDs automatically using
            # autoincrement.
            empty_ids = [None] * len(splitted["data"])

            rows = []
            for id, values in zip(empty_ids, splitted["data"]):
                rows.append([id, *values])

            return rows


class CopyMultipleGenresMoviesToSQLite(luigi.WrapperTask):
    """Download top-50 movies by multiple `genres` and load them into SQLite.

    Each genre gets a separate database table.
    """

    genres = luigi.parameter.EnumListParameter(enum=Genre)

    def requires(self):
        for genre in self.genres:
            yield CopyMoviesToSQLite(genre=genre)
