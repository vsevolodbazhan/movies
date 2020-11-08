from enum import Enum, auto, unique
from typing import Any, List


class AutoGenreName(Enum):
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: List[Any]
    ) -> Any:
        return name.lower()


@unique
class Genre(AutoGenreName):
    """Movie genres available on IMDb."""

    ACTION = auto()
    ADVENTURE = auto()
    ANIMATION = auto()
    BIOGRAPHY = auto()
    COMEDY = auto()
    CRIME = auto()
    DOCUMENTARY = auto()
    DRAMA = auto()
    FAMILY = auto()
    FANTASY = auto()
    FILMNOIR = "film noir"
    HISTORY = auto()
    HORROR = auto()
    MUSIC = auto()
    MUSICAL = auto()
    MYSTERY = auto()
    ROMANCE = auto()
    SCIFI = "sci-fi"
    SHORT = auto()
    SPORT = auto()
    SUPERHERO = auto()
    THRILLER = auto()
    WAR = auto()
    WESTERN = auto()
