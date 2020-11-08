from dataclasses import astuple, dataclass, fields
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup, ResultSet

from .genres import Genre

__all__ = ["Movie", "get_top_movies"]


@dataclass
class Movie:
    """Movie parameters."""

    title: str
    genre: str
    rating: float
    year: int
    runtime: int
    votes: int
    metascore: Optional[int]
    certificate: Optional[str]
    gross: Optional[float]

    @property
    def data(self):
        return astuple(self)

    @property
    def fields(self):
        return fields(self)


def create_page_url(genre: Genre) -> str:
    """Generate IMDb page URL using given genre."""

    return f"https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&genres={genre.value}&sort=user_rating,desc&view=detailed"  # noqa: 501


def download_top_movies(genre: Genre) -> str:
    """Download HTML markup for top-50 movies by genre."""

    page_url = create_page_url(genre)
    response = requests.get(page_url)
    response.raise_for_status()
    return response.text


def parse_top_movies(html: str) -> ResultSet:
    """Parse downloaded HTML into `BeautifulSoup` object."""

    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("div", class_="lister-item-content")


def extract_movie_header(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract movie title and year from `BeautifulSoup` object."""

    header = soup.find("h3", class_="lister-item-header")

    title = header.a.get_text()

    year = header.find("span", class_="lister-item-year").get_text()[-5:-1]
    year = int(year)

    return title, year


def extract_movie_meta(soup: BeautifulSoup) -> Tuple[int, str, Optional[str]]:
    """Extract movie runtime and certificate (if present) from `BeautifulSoup` object."""

    meta = soup.find("p", class_="text-muted")

    runtime_with_suffix = meta.find("span", class_="runtime").get_text()
    runtime = runtime_with_suffix[:-4]
    runtime = int(runtime)

    certificate = None
    if certificate_element := meta.find("span", class_="certificate"):
        certificate = certificate_element.get_text()

    return runtime, certificate


def extract_movie_rating_bar(soup: BeautifulSoup) -> Tuple[float, Optional[int]]:
    """Extract movie rating and metascore (if present) from `BeautifulSoup` object."""

    rating_bar = soup.find("div", class_="ratings-bar")

    rating = rating_bar.strong.get_text()
    rating = float(rating)

    metascore = None
    if metascore_element := rating_bar.find("span", class_="metascore favorable"):
        metascore = metascore_element.get_text()
        metascore = int(metascore)

    return rating, metascore


def extract_movie_extra(soup: BeautifulSoup) -> Tuple[int, Optional[float]]:
    """Extract movie votes and gross (if present) from `BeautifulSoup`  object."""

    extra = soup.find("p", class_="sort-num_votes-visible")
    extra_elements = extra.find_all("span", attrs={"name": "nv"})

    votes = extra_elements[0]["data-value"].replace(",", "")
    votes = int(votes)

    try:
        gross = extra_elements[1]["data-value"].replace(",", "")
        gross = float(gross)
    except IndexError:
        gross = None

    return votes, gross


def extract_movie(soup: BeautifulSoup, genre: Genre) -> Movie:
    """Extract movie of with `genre` from `BeautifulSoup` object into `Movie` dataclass."""

    title, year = extract_movie_header(soup)
    runtime, certificate = extract_movie_meta(soup)
    rating, metascore = extract_movie_rating_bar(soup)
    votes, gross = extract_movie_extra(soup)

    return Movie(
        title, genre.value, rating, year, runtime, votes, metascore, certificate, gross
    )


def get_top_movies(genre: Genre) -> List[Movie]:
    """Download and parse top-50 movies into a list of `Movie` dataclasses."""

    html = download_top_movies(genre)
    soup = parse_top_movies(html)
    return [extract_movie(result, genre) for result in soup]
