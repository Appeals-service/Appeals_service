from fastapi import APIRouter, status, Depends, Request, Response

from dto.schemas.users import UserCreate, RefreshToken
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/registration",
    response_model=RefreshToken,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
)
async def register(request: Request, response: Response, user_data: UserCreate = Depends()):
    return await UserService.register(user_data, request.headers["user-agent"], response)
