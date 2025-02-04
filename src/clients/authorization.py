from src.clients.base import BaseAsyncClient
from src.common.settings import settings


class AuthorizationClient(BaseAsyncClient):

    async def register(self, user_data: dict) -> tuple:
        async with self._post(path="/api/v1/users/registration", json=user_data) as response:
            return response.status, await response.json()

    async def login(self, user_data: dict) -> tuple:
        async with self._post(path="/api/v1/users/login", json=user_data) as response:
            return response.status, await response.json()

    async def logout(self, cookies: dict, user_agent: str) -> tuple:
        async with self._post(path="/api/v1/users/logout", cookies=cookies, data=user_agent) as response:
            return response.status, await response.json()

    async def refresh(self, user_data: dict) -> tuple:
        async with self._post(path="/api/v1/users/refresh", json=user_data) as response:
            return response.status, await response.json()

    async def me(self, cookies: dict) -> tuple:
        async with self._get(path="/api/v1/users/me", cookies=cookies) as response:
            return response.status, await response.json()

authorization_client = AuthorizationClient(settings.AUTHORIZATION_SERVICE_URL, settings.AUTHORIZATION_SERVICE_TIMEOUT)
