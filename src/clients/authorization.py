from src.clients.base import BaseAsyncClient

from src.common.settings import settings


class AuthorizationClient(BaseAsyncClient):

    async def register(self, user_data: dict):
        async with self._post(path="/api/v1/users/registration", json=user_data) as response:
            return await response.json()

    async def login(self, user_data: dict):
        async with self._post(path="/api/v1/users/login", json=user_data) as response:
            return await response.json()

authorization_client = AuthorizationClient(settings.AUTHORIZATION_SERVICE_URL, settings.AUTHORIZATION_SERVICE_TIMEOUT)
