from abc import ABC, abstractmethod


class BaseStorage (ABC):

    @abstractmethod
    async def save_data(self, key: str, data: dict) -> None:
        """Save state to storage."""
        pass

    @abstractmethod
    async def retrieve_data(self, key: str) -> dict:
        """Load state locally from storage."""
        pass
