from models.mixins import OrjsonMixin
from models.person import Person
from pydantic import Field, validator


class Film(OrjsonMixin):
    """Структура данных соответствующая index поиска Elasticsearch."""
    id: str
    imdb_rating: float | None = Field(default=0.0)
    genre: list[str]
    title: str
    description: str | None = Field(default=None)
    director: list[str]
    actors: list[Person]
    writers: list[Person]
    actors_names: str
    writers_names: list[str]

    @validator('description')
    def set_description(cls, description):
        return description or ''


class FilmPages(OrjsonMixin):
    """Паджинация фильмов."""
    first: int | None = 1
    last: int
    prev: int | None = None
    next: int | None = None
    data: list[Film]
