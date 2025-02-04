from fastapi import APIRouter, status, Depends, Request, Response, Body

from dto.schemas.users import UserCreate, RefreshToken, UserAuth, UserBase
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/registration",
    response_model=RefreshToken,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
    response_description="Tokens in cookie and body"
)
async def register(request: Request, response: Response, user_data: UserCreate):
    return await UserService.register(user_data, request.headers["user-agent"], response)


@router.post(
    "/login",
    response_model=RefreshToken,
    summary="User login",
    response_description="Tokens in cookie and body",
)
async def login(request: Request, response: Response, user_data: UserAuth):
    return await UserService.login(user_data, request.headers["user-agent"], response)

@router.post(
    "/logout",
    summary="User logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(request: Request, response: Response):
    await UserService.logout(request, response)


@router.post(
    "/refresh",
    response_model=RefreshToken,
    summary="Refresh tokens",
    response_description="Tokens in cookie and in body",
)
async def refresh_tokens(request: Request, response: Response, refresh_token: str = Body()):
    return await UserService.refresh(refresh_token, request.headers["user-agent"], response)

@router.get(
    "/me",
    response_model=UserBase,
    summary="Get current user data",
    response_description="User data",
)
async def get_user_data(request: Request):
    return await UserService.me(request.cookies)


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete(request: Request, user_id: str = Body()):
    return await UserService.delete(request.cookies, user_id)
