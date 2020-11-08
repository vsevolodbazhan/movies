from dataclasses import dataclass
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup, ResultSet

__all__ = ["Movie", "download_top_movies", "extract_top_movies", "extract_movie"]


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


def create_page_url(genre: str) -> str:
    """Generate IMDb page URL using given genre."""

    return f"https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&genres={genre}&sort=user_rating,desc&view=detailed"  # noqa: 501


def download_top_movies(genre: str) -> str:
    """Download HTML markup for top-50 movies by genre."""

    page_url = create_page_url(genre)
    response = requests.get(page_url)
    response.raise_for_status()
    return response.text


def parse_top_movies(html: str) -> ResultSet:
    """Parse downloaded HTML into BeautifulSoup object."""

    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("div", class_="lister-item-content")


def extract_movie_header(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract movie title and year from BeautifulSoup object."""

    header = soup.find("h3", class_="lister-item-header")

    title = header.a.get_text()

    year = header.find("span", class_="lister-item-year").get_text()[-5:-1]
    year = int(year)

    return title, year


def extract_movie_meta(soup: BeautifulSoup) -> Tuple[int, str, Optional[str]]:
    """Extract movie runtime, genre, certificate (if present) from BeautifulSoup object."""

    meta = soup.find("p", class_="text-muted")

    runtime_with_suffix = meta.find("span", class_="runtime").get_text()
    runtime = runtime_with_suffix[:-4]
    runtime = int(runtime)

    genres = meta.find("span", class_="genre").get_text()
    genre = genres.split(", ")[0].lstrip("\n")

    certificate = None
    if certificate_element := meta.find("span", class_="certificate"):
        certificate = certificate_element.get_text()

    return runtime, genre, certificate


def extract_movie_rating_bar(soup: BeautifulSoup) -> Tuple[float, Optional[int]]:
    """Extract movie rating and metascore (if present) from BeautifulSoup object."""

    rating_bar = soup.find("div", class_="ratings-bar")

    rating = rating_bar.strong.get_text()
    rating = float(rating)

    metascore = None
    if metascore_element := rating_bar.find("span", class_="metascore favorable"):
        metascore = metascore_element.get_text()
        metascore = int(metascore)

    return rating, metascore


def extract_movie_extra(soup: BeautifulSoup) -> Tuple[int, Optional[float]]:
    """Extract movie votes and gross (if present) from BeautifulSoup object."""

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


def extract_movie(soup: BeautifulSoup) -> Movie:
    """Extract movie info from BeautifulSoup object into Movie dataclass."""

    title, year = extract_movie_header(soup)
    runtime, genre, certificate = extract_movie_meta(soup)
    rating, metascore = extract_movie_rating_bar(soup)
    votes, gross = extract_movie_extra(soup)

    return Movie(
        title, genre, rating, year, runtime, votes, metascore, certificate, gross
    )
