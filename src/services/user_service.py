from fastapi import Response, HTTPException, status, Request

from src.clients.authorization import authorization_client
from src.dto.schemas.users import UserCreate, UserAuth


class UserService:

    @staticmethod
    async def register(user_data: UserCreate, user_agent: str, response: Response) -> dict:
        user_data_dict = user_data.model_dump()
        user_data_dict.update({"user_agent": user_agent})
        response_status, response_dict = await authorization_client.register(user_data_dict)

        if response_status != status.HTTP_201_CREATED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_dict)

        if not response_dict or not response_dict.get("access_token") or not response_dict.get("refresh_token"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tokens have not been created")

        response.set_cookie(key="access_token", value=response_dict.get("access_token"), httponly=True)
        return dict(refresh_token=response_dict.get("refresh_token"))

    @classmethod
    async def login(cls, user_data: UserAuth, user_agent: str, response: Response) -> dict:
        user_data_dict = user_data.model_dump()
        user_data_dict.update({"user_agent": user_agent})
        response_status, response_dict = await authorization_client.login(user_data_dict)

        if response_status != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_dict)

        if not response_dict or not response_dict.get("access_token") or not response_dict.get("refresh_token"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tokens have not been created")

        response.set_cookie(key="access_token", value=response_dict.get("access_token"), httponly=True)
        return dict(refresh_token=response_dict.get("refresh_token"))

    @classmethod
    async def logout(cls, request: Request, response: Response) -> None:
        response_status, response_dict = await authorization_client.logout(
            request.cookies, request.headers["user-agent"]
        )

        if response_status != status.HTTP_204_NO_CONTENT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_dict)

        response.delete_cookie(key="access_token", httponly=True)

    @classmethod
    async def refresh(cls, refresh_token: str, user_agent: str, response: Response) -> dict:
        response_status, response_dict = await authorization_client.refresh(
            {"refresh_token": refresh_token, "user_agent": user_agent}
        )

        if response_status != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_dict)

        response.set_cookie(key="access_token", value=response_dict.get("access_token"), httponly=True)
        return dict(refresh_token=response_dict.get("refresh_token"))

    @classmethod
    async def me(cls, cookies: dict) -> dict:
        response_status, response_dict = await authorization_client.me(cookies)

        if response_status != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_dict)

        return response_dict
