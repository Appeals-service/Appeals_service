from fastapi import APIRouter, Body, Request, Response, status

from dto.schemas.users import RefreshToken, UserAuth, UserBase, UserCreate, UserListResponse
from services.user import UserService
from utils.cache import cache
from utils.enums import UserRole

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
@cache(expire=60)
async def get_user_data(request: Request):
    return await UserService.get_me(request.cookies)


@router.get(
    "/list",
    response_model=list[UserListResponse],
    summary="Get users list",
    response_description="Users list",
)
async def get_users_list(request: Request, role: UserRole | None = None):
    return await UserService.get_list(request.cookies, role)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete(request: Request, user_id: str):
    return await UserService.delete(request.cookies, user_id)
