from fastapi import APIRouter, Depends, status
from sqlalchemy.engine.row import Row

from dto.schemas.appeals import (
    AppealCreate,
    AppealListFilters,
    AppealListResponse,
    AppealResponse,
    ExecutorAppealUpdate,
    UserAppealUpdate,
)
from dto.schemas.users import JWTUserData
from services.appeal import AppealService
from utils.cache import cache
from utils.role_checker import allowed_for_admin_executor, allowed_for_admin_user, allowed_for_all

router = APIRouter(prefix="/appeals", tags=["Appeal"])


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create appeal")
async def create(
        appeal_data: AppealCreate = Depends(), user_data: JWTUserData = Depends(allowed_for_admin_user)
) -> None:
    return await AppealService.create(appeal_data, user_data.id)


@router.get("/", response_model=list[AppealListResponse], summary="Get appeals list")
@cache()
async def get_appeals_list(
        filters: AppealListFilters = Depends(), user_data: JWTUserData = Depends(allowed_for_all)
) -> list[Row]:
    return await AppealService.get_appeals_list(filters, user_data)


@router.get("/{appeal_id}", response_model=AppealResponse, summary="Get appeal detail")
@cache()
async def get_appeal(appeal_id: int, user_data: JWTUserData = Depends(allowed_for_all)) -> Row:
    return await AppealService.get_appeal(appeal_id, user_data)


@router.patch("/{appeal_id}/user", response_model=AppealResponse | None, summary="User's update appeal")
async def users_update(
        appeal_id: int,
        user_upd_data: UserAppealUpdate = Depends(),
        user_data: JWTUserData = Depends(allowed_for_admin_user),
) -> Row | None:
    return await AppealService.users_update(appeal_id, user_upd_data, user_data)


@router.patch("/{appeal_id}/executor", response_model=AppealResponse | None, summary="Executor's update appeal")
async def executors_update(
        appeal_id: int,
        executor_upd_data: ExecutorAppealUpdate = Depends(),
        user_data: JWTUserData = Depends(allowed_for_admin_executor),
) -> Row | None:
    return await AppealService.executors_update(appeal_id, executor_upd_data, user_data)



@router.delete("/{appeal_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete appeal")
async def delete(appeal_id: int, user_data: JWTUserData = Depends(allowed_for_admin_user)) -> None:
    return await AppealService.delete(appeal_id, user_data)


@router.patch(
    "/{appeal_id}/assign",
    response_model=AppealResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Assign a executor",
)
async def executor_assign(
        appeal_id: int,
        executor_id: str | None = None,
        user_data: JWTUserData = Depends(allowed_for_admin_executor),
) -> Row:
    return await AppealService.executor_assign(appeal_id, executor_id, user_data)
