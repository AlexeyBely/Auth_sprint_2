from abc import ABC, abstractmethod


class DBConnector(ABC):
    @abstractmethod
    def __init__(self, host, port):
        pass

    @abstractmethod
    async def get(self, source, item_id):
        pass

    @abstractmethod
    async def get_page(self, source, size, page, sort):
        pass

    @abstractmethod
    async def search(self, source, query, size, page, sort):
        pass

    @abstractmethod
    async def close(self):
        pass


db_connector: DBConnector | None = None


def get_db_connector() -> DBConnector:
    if db_connector is None:
        raise ValueError('The DB connector is not set')
    return db_connector
