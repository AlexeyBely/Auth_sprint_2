from typing import Type

from api.v1.response_models import PaginatedListMixin
from core import messages
from core.config import api_settings
from db.db_connector import DBConnector
from pydantic import BaseModel
from services.utils import compute_page_numbers


class BaseService:
    """
    Base service class.

    Attributes:
        default_response_item_class     The default pydantic class to return a single record
        default_response_list_class     The default pydantic class to return a list of records
        default_db_source               The default DB source name (table name, index, etc...)
    """
    default_response_item_class = None
    default_response_list_class = None
    default_db_source = None

    def __init__(self, connector: DBConnector):
        self.connector = connector

    def get_default_response_item_class(self):
        if self.default_response_item_class is None:
            raise NotImplementedError(messages.ERROR_RESPONSE_ITEM_CLASS_UNDEFINED)
        return self.default_response_item_class

    def get_default_response_list_class(self):
        if self.default_response_list_class is None:
            raise NotImplementedError(messages.ERROR_RESPONSE_LIST_CLASS_UNDEFINED)
        return self.default_response_list_class

    def get_default_db_source(self):
        if self.default_db_source is None:
            raise NotImplementedError(messages.ERROR_ES_INDEX_NAME_UNDEFINED)
        return self.default_db_source

    def handle_list_response(self, response_data: dict, size: int, page: int, item_class: Type[BaseModel] | None = None,
                             list_class: Type[PaginatedListMixin] | None = None) -> PaginatedListMixin | Type[PaginatedListMixin]:
        """
        Helps to paginate response.

        :param response_data: ElasticSearch response
        :param size: a number of instances to return.
        :param page: a page number
        :param item_class: Pydantic class for every one item.
        :param list_class: Pydantic class for the list with page numbers.
        :return:
        """
        if item_class is None:
            item_class = self.get_default_response_item_class()
        if list_class is None:
            list_class = self.get_default_response_list_class()
        records = response_data.get('hits', {}).get('hits', [])
        items = [item_class(**r['_source']) for r in records]
        total = response_data.get('hits', {}).get('total', {}).get('value', 0)
        page_numbers = compute_page_numbers(page, size, total)
        return list_class(data=items, **page_numbers)

    async def get_by_id(self, item_id: str, source: str | None = None) -> Type[BaseModel] | None:
        """
        Returns instance by id (or None if not found) specified as item_id parameter.

        :param item_id: item uuid.
        :param source: DB source (table name, index, etc...).
        :return: found instance or None.
        """
        if source is None:
            source = self.get_default_db_source()
        data = await self.connector.get(item_id=item_id, source=source)
        if data is None:
            return None
        item_class = self.get_default_response_item_class()
        return item_class(**data)

    async def get_list(self, size: int = api_settings.default_response_page_size, page: int = 1,
                       sort: str | None = None, source: str | None = None) -> Type[PaginatedListMixin]:
        """
        Returns list of instances.

        :param size: a number of instances to return.
        :param page: a page number
        :param sort: a comma-separated list of <field>:<direction> pairs. Note: not all field types can be sorted.
        :param source: DB source (table name, index, etc...).
        :return:
        """
        if source is None:
            source = self.get_default_db_source()
        response = await self.connector.get_page(source=source, size=size, page=page, sort=sort)
        return self.handle_list_response(response, size, page)

    async def search(self, query: str | dict, size: int, page: int, sort: int,
                     source: str | None = None) -> Type[PaginatedListMixin]:
        if source is None:
            source = self.get_default_db_source()
        response = await self.connector.search(source=source, query=query, size=size, page=page, sort=sort)
        return self.handle_list_response(response, size, page)
