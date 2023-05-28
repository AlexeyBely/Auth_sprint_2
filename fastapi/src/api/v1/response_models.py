from enum import Enum

from core.config import api_settings
from models.mixins import OrjsonMixin
from pydantic import BaseModel, Field

from fastapi import Query


# Mixins

class PaginatedParams(BaseModel):
    size: int = Query(api_settings.default_response_page_size, description='page[size]', ge=1, le=api_settings.max_page_size)
    page: int = Query(1, description='page[number]', ge=1)


class PaginatedListMixin(OrjsonMixin):
    prev: int | None
    next: int | None
    first: int | None
    last: int | None
    data: list  # list of objects


# Selection helpers

class FilmSortSelection(str, Enum):
    rating_asc = 'imdb_rating:asc'
    rating_desc = 'imdb_rating:desc'


class GenreSortSelection(str, Enum):
    name_asc = 'name:asc'
    name_desc = 'name:desc'


class PersonSortSelection(str, Enum):
    full_name_asc = 'full_name:asc'
    full_name_desc = 'full_name:desc'


# Models

class FilmShortResponse(OrjsonMixin):
    id: str
    title: str
    imdb_rating: float


class FilmShortListResponse(PaginatedListMixin):
    data = list[FilmShortResponse]


class GenreResponse(OrjsonMixin):
    id: str
    name: str
    description: str


class GenreListResponse(PaginatedListMixin):
    data: list[GenreResponse]


class PersonResponse(OrjsonMixin):
    id: str
    full_name: str = Field(alias='name')

    class Config:
        allow_population_by_field_name = True


class PersonListResponse(PaginatedListMixin):
    data: list[PersonResponse]


# Film models

class FilmResponse(OrjsonMixin):
    id: str
    imdb_rating: float
    genres: list = Field(alias='genre')
    title: str
    description: str | None = None
    directors: list = Field(alias='director')
    actors: list[PersonResponse]
    writers: list[PersonResponse]


class FilmsListResponse(PaginatedListMixin):
    data: list[FilmShortResponse]
