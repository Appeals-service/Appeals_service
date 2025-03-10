from clients.http.base import BaseAsyncClient
from common.settings import settings
from utils.enums import UserRole


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

    async def get_me(self, cookies: dict) -> tuple:
        async with self._get(path="/api/v1/users/me", cookies=cookies) as response:
            return response.status, await response.json()

    async def get_list(self, cookies: dict, role: UserRole | None = None) -> tuple:
        params = {"role": role} if role else None
        async with self._get(path="/api/v1/users/list", params=params, cookies=cookies) as response:
            return response.status, await response.json()

    async def get_user_email(self, user_id: str) -> tuple:
        async with self._get(path=f"/api/v1/users/{user_id}/email") as response:
            return response.status, await response.text()

    async def delete(self, cookies: dict, user_id: str) -> tuple:
        async with self._delete(path=f"/api/v1/users/{user_id}", cookies=cookies) as response:
            return response.status, await response.json()

authorization_client = AuthorizationClient(settings.AUTHORIZATION_SERVICE_URL, settings.AUTHORIZATION_SERVICE_TIMEOUT)
