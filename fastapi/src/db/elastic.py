from db.db_connector import DBConnector
from elasticsearch import AsyncElasticsearch, NotFoundError


class ElasticSearchConnector(DBConnector):
    RAW_SORT_FIELDS = {
        'persons': ['full_name'],
        'movies': ['title'],
    }

    def _get_raw_sort_fields(self, source: str) -> list:
        return self.RAW_SORT_FIELDS.get(source, [])

    def _handle_sort(self, source: str, sort: str | None) -> str | None:
        """
        Helps to change sort parameter for text fields which have raw subfield for sorting.
        """
        if sort is None:
            return None
        for field_name in self._get_raw_sort_fields(source):
            field, order = sort.split(':')
            if field == field_name:
                # we need to use inner 'raw' keyword field, because main field has type text
                return f'{field_name}.raw:{order}'
        return sort

    def _prepare_search_query(self, source: str, query: str | dict, size: int, page: int, sort: str) -> dict:
        offset = (page - 1) * size
        body = {'query': query, 'from': offset, 'size': size}
        response_data = {'index': source, 'body': body}
        sort = self._handle_sort(source, sort)
        if sort is not None:
            response_data['sort'] = sort
        return response_data

    def __init__(self, host: str, port: int) -> None:
        """
        Initialize a database connection.
        """
        self.connector = AsyncElasticsearch(hosts=[f'{host}:{port}'])

    async def get(self, source: str, item_id: str) -> dict | None:
        """
        Get a single record from a database source.

        :param source: a source of database (table name, index, etc.)
        :param item_id: an identifier to get the record.
        """
        try:
            doc = await self.connector.get(source, item_id)
        except NotFoundError:
            return None
        return doc['_source']

    async def get_page(self, source: str, size: int, page: int, sort: str) -> dict:
        """
        Returns a list of records on defined page.

        :param source: a source of database (table name, index, etc.).
        :param size: a number of records per page.
        :param page: the page number
        :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
        :return: a list of records on defined page.
        """
        query = {'match_all': {}}
        response_data = self._prepare_search_query(source, query, size, page, sort)
        return await self.connector.search(**response_data)

    async def search(self, source: str, query: str, size: int, page: int, sort: str) -> dict:
        """
        Search for records satisfied the search query.

        :param source: a source of database (table name, index, etc.).
        :param query: a search query.
        :param size: a number of records per page.
        :param page: the page number
        :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
        :return: a list of found records on defined page.
        """
        response_data = self._prepare_search_query(source, query, size, page, sort)
        return await self.connector.search(**response_data)

    async def close(self):
        """
        Close a database connection.
        """
        return await self.connector.close()
