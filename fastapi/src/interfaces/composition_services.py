from functools import lru_cache
from typing import Type

from db.db_connector import DBConnector, get_db_connector
from services.film import FilmService
from services.genre import GenreService
from services.person import PersonService

from fastapi import Depends


@lru_cache()
def get_film_service(db_connector: DBConnector = Depends(get_db_connector)) -> Type[FilmService]:
    """interface and film service connectivity."""
    return FilmService(db_connector)


@lru_cache()
def get_genre_service(db_connector: DBConnector = Depends(get_db_connector)) -> Type[GenreService]:
    """interface and genre service connectivity."""
    return GenreService(db_connector)


@lru_cache()
def get_person_service(db_connector: DBConnector = Depends(get_db_connector)) -> Type[PersonService]:
    """interface and person service connectivity."""
    return PersonService(db_connector)
