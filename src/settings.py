from pydantic import BaseSettings

__all__ = ["settings"]


class Settings(BaseSettings):
    MOVIE_DATA_DIR = "movies"

    MONGO_HOST = "localhost"
    MONGO_PORT = 27017
    MONGO_INDEX = "movies"
    MONGO_COLLECTION = "top_movies"

    class Config:
        case_sensitive = True


settings = Settings()
