from fastapi import Response, HTTPException, status

from src.clients.authorization import authorization_client
from src.dto.schemas.users import UserCreate


class UserService:

    @staticmethod
    async def register(user_data: UserCreate, user_agent: str, response: Response) -> dict:
        dict_user_data = user_data.model_dump()
        dict_user_data.update({"user_agent": user_agent})
        tokens = await authorization_client.register(dict_user_data)

        if not tokens or not tokens.get("access_token") or not tokens.get("refresh_token"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tokens have not been created")

        response.set_cookie(key="access_token", value=tokens.get("access_token"), httponly=True)
        return dict(refresh_token=tokens.get("refresh_token"))
