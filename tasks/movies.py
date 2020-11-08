import luigi
import requests
from bs4 import BeautifulSoup


def create_page_url(genre):
    return f"https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&genres={genre}&sort=user_rating,desc&view=detailed"  # noqa: 501


def download_top50_movies(genre):
    page_url = create_page_url(genre)
    response = requests.get(page_url)
    response.raise_for_status()
    return response.text


class LoadTop50Movies(luigi.Task):
    genre = luigi.Parameter()
