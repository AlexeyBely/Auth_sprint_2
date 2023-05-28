from api.v1.response_models import FilmResponse, FilmsListResponse
from models.film import Film
from services.base import BaseService
from services.cache import cache_es
from services.genre import GenreService


class FilmService(BaseService):
    default_response_item_class = FilmResponse
    default_response_list_class = FilmsListResponse
    default_db_source = 'movies'

    @cache_es(FilmResponse)
    async def get_by_id(self, film_id: str, source: str | None = None) -> Film | None:
        """Поиск по uuid фильма."""
        return await super().get_by_id(film_id, source)

    @cache_es(FilmsListResponse)
    async def search(self, query: str, page: int, size: int, sort: str,
                     source: str | None = None) -> FilmsListResponse | None:
        """Поиск по title фильма."""
        search_query = {'match': {'title': {'query': query}}}
        return await super().search(search_query, size, page, sort, source)

    @cache_es(FilmsListResponse)
    async def get_list(self, sort: str, filter: str | None, page: int, size: int,
                       source: str | None = None) -> FilmsListResponse | None:
        """Поиск по жанру фильма и сортировка."""
        if filter is not None:
            genre_service = GenreService(self.connector)
            genre = await genre_service.get_by_id(filter)
            if genre is None:
                return None
            query = {'match': {'genre': {'query': genre.name}}}
        else:
            query = {'match_all': {}}
        return await super().search(query, size, page, sort, source)
