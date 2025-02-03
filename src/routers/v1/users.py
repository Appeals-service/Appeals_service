from fastapi import APIRouter, status, Depends, Request, Response

from dto.schemas.users import UserCreate, RefreshToken, UserAuth
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/registration",
    response_model=RefreshToken,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
    response_description="Tokens in cookie and body"
)
async def register(request: Request, response: Response, user_data: UserCreate = Depends()):
    return await UserService.register(user_data, request.headers["user-agent"], response)


@router.post(
    "/login",
    response_model=RefreshToken,
    summary="User login",
    response_description="Tokens in cookie and body",
)
async def login(request: Request, response: Response, user_data: UserAuth = Depends()):
    return await UserService.login(user_data, request.headers["user-agent"], response)

@router.post(
    "/logout",
    summary="User logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(request: Request, response: Response):
    await UserService.logout(request, response)
