import csv
import glob
import os
from ast import literal_eval

import luigi
import pandas as pd
from luigi.contrib.mongodb import MongoCollectionTarget
from luigi.util import requires
from pymongo import MongoClient

from .genres import Genre
from .movies import get_top_movies
from .settings import settings


class LoadTopMoviesByGenre(luigi.Task):
    """Download top-50 movies by `genre` and store them in .csv file."""

    genre = luigi.EnumParameter(enum=Genre)

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
        return luigi.LocalTarget(os.path.join(settings.MOVIE_DATA_DIR, self.file_name))


class LoadTopMoviesByMultipleGenre(luigi.WrapperTask):
    """Download top-50 movies of each genre in `genres` and store them in .csv file."""

    genres = luigi.parameter.EnumListParameter(enum=Genre)

    def requires(self):
        for genre in self.genres:
            yield LoadTopMoviesByGenre(genre=genre)


@requires(LoadTopMoviesByMultipleGenre)
class CopyMoviesToMongoDB(luigi.Task):
    """Download and load top-50 movies of each genre in `genres` to MongoDB.

    Movies are sorted by IMDb rating and title.
    """

    def run(self):
        output = self.output().get_collection()

        df = self._read_all_movies_files()
        df.sort_values(by=["rating", "title"])

        documents = df.to_dict(orient="records")
        output.insert_many(documents)

    def output(self):
        client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        return MongoCollectionTarget(
            client, settings.MONGO_INDEX, settings.MONGO_COLLECTION
        )

    def _read_all_movies_files(self):
        files = glob.glob(os.path.join(settings.MOVIE_DATA_DIR, "*.csv"))
        return pd.concat(self._read_movies_file(f) for f in files)

    def _read_movies_file(self, filename):
        return pd.read_csv(filename, converters={"genres": literal_eval})
