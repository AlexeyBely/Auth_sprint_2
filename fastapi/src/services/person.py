from api.v1.response_models import (FilmShortListResponse, FilmShortResponse,
                                    PersonListResponse, PersonResponse)
from core.config import api_settings
from services.base import BaseService
from services.cache import cache_es
from services.film import FilmService


class PersonService(BaseService):
    default_response_item_class = PersonResponse
    default_response_list_class = PersonListResponse
    default_db_source = 'persons'

    @cache_es(PersonResponse)
    async def get_by_id(self, person_id: str, source: str | None = None) -> PersonResponse | None:
        return await super().get_by_id(person_id, source)

    @cache_es(PersonListResponse)
    async def get_list(self, size: int = api_settings.default_response_page_size, page: int = 1,
                       sort: str | None = None, source: str | None = None) -> PersonListResponse:
        return await super().get_list(size, page, sort, source)

    @cache_es(FilmShortListResponse)
    async def get_person_films(self, person_id: str, size: int = api_settings.default_response_page_size, page: int = 0,
                               sort: str = 'imdb_rating:desc') -> FilmShortListResponse | None:
        """
        Returns films in which the person with the person_id UUID participated.

        :param person_id: person id
        :param size: the film number per page
        :param page: the page number
        :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
        :return: the list of films and page numbers for pagination
        """
        person = await self.get_by_id(person_id)
        # persons = await self.get_list()
        if not person:
            return None
        search_query = {
            'bool': {
                'must': [
                    {'query_string': {'query': f'"{person.full_name}"'}}
                ],
                'should': [
                    {'nested': {'path': 'actors', 'query': {"match": {'actors.id': person_id}}}},
                    {'nested': {'path': 'writers', 'query': {"match": {'writers.id': person_id}}}},
                ]
            }
        }
        film_service = FilmService(self.connector)
        response = await film_service.search(search_query, size, page, sort)
        return self.handle_list_response(response, size, page, FilmShortResponse, FilmShortListResponse)

        offset = (page - 1) * size
        person = await self.get_by_id(person_id)
        if not person:
            return None
        response = await self.elastic.search(
            index='movies',
            body={
                'query': {
                    'bool': {
                        'must': [
                            {'query_string': {'query': f'"{person.full_name}"'}}
                        ],
                        'should': [
                            {'nested': {'path': 'actors', 'query': {"match": {'actors.id': person_id}}}},
                            {'nested': {'path': 'writers', 'query': {"match": {'writers.id': person_id}}}},
                        ]
                    }},
                'from': offset,
                'size': size
            },
            sort=sort
        )
        return self.handle_list_response(response, size, page, FilmShortResponse, FilmShortListResponse)

    @cache_es(PersonResponse)
    async def search(self, query: str, size: int = api_settings.default_response_page_size, page: int = 1,
                     sort: str = 'full_name:asc', source: str | None = None) -> PersonListResponse:
        """
        Search for persons by full_name field.

        :param query: the search phrase
        :param size: the person number per page
        :param page: the page number
        :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
        :param source: DB source (table name, index, etc...).
        :return: persons found
        """
        search_query = {'match': {'full_name': {'query': query}}}
        return await super().search(search_query, size, page, sort, source)
