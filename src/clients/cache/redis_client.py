from redis.asyncio.client import Redis, Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError

from clients.cache.abstract_client import AbstractCacheClient
from common.settings import settings


class RedisClient(AbstractCacheClient):

    _client: Redis | None = None

    def __init__(self):
        self._client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            socket_timeout=3,
            retry=Retry(ExponentialBackoff(), 3),
            retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
            decode_responses=True,
            auto_close_connection_pool=True,
        )

    async def disconnect(self):
        await self._client.aclose(close_connection_pool=True)

    async def set(self, key: str, value: str, expire: int) -> None:
        await self._client.set(name=key, value=value, ex=expire)

    async def get(self, key: str,) -> str:
        return await self._client.get(name=key)

redis_client = RedisClient()
