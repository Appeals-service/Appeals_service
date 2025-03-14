from abc import ABC, abstractmethod


class AbstractCacheClient(ABC):

    @abstractmethod
    async def get(self, key: str):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int):
        pass
