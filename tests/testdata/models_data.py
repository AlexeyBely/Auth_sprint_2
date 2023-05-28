from pydantic import BaseModel, Field


class FilmPerson(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    imdb_rating: float | None = Field(default=0.0)
    genre: list[str]
    title: str
    description: str | None = Field(default=None)
    director: list[str]
    actors: list[FilmPerson]
    writers: list[FilmPerson]
    actors_names: str | None = None
    writers_names: list[str] | None = None


class FilmShort(BaseModel):
    id: str
    title: str
    imdb_rating: float


class Genre(BaseModel):
    id: str
    name: str
    description: str


class Person(BaseModel):
    id: str
    full_name: str = Field(..., alias='name')
