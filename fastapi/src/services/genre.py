from api.v1.response_models import GenreListResponse, GenreResponse
from core.config import api_settings
from services.base import BaseService
from services.cache import cache_es


class GenreService(BaseService):
    default_response_item_class = GenreResponse
    default_response_list_class = GenreListResponse
    default_db_source = 'genres'

    @cache_es(GenreResponse)
    async def get_by_id(self, genre_id: str, source: str | None = None) -> GenreResponse | None:
        return await super().get_by_id(genre_id, source)

    @cache_es(GenreListResponse)
    async def get_list(self, size: int = api_settings.default_response_page_size, page: int = 0,
                       sort: str | None = None, source: str | None = None) -> GenreListResponse:
        return await super().get_list(size, page, sort, source)
