from fastapi import APIRouter, status, Depends
from sqlalchemy.engine.row import Row

from dto.schemas.appeals import AppealCreate, AppealListFilters, AppealListResponse, AppealResponse, UserAppealUpdate, \
    ExecutorAppealUpdate
from services.appeal import AppealService
from src.utils.role_checker import allowed_for_admin_user, allowed_for_all, allowed_for_admin_executor
from utils.enums import UserRole

router = APIRouter(prefix="/appeals", tags=["Appeal"])


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create appeal")
async def create(
        appeal_data: AppealCreate = Depends(), role_n_id: tuple[UserRole, str] = Depends(allowed_for_admin_user)
) -> None:
    return await AppealService.create(appeal_data, role_n_id[1])


@router.get("/", response_model=list[AppealListResponse], summary="Get appeals list")
async def get_appeals_list(
        filters: AppealListFilters = Depends(), role_n_id: tuple[UserRole, str] = Depends(allowed_for_all)
) -> list[Row]:
    return await AppealService.get_appeals_list(filters, role_n_id)


@router.get("/{appeal_id}", response_model=AppealResponse, summary="Get appeal detail")
async def get_appeal(appeal_id: int, role_n_id: tuple[UserRole, str] = Depends(allowed_for_all)) -> Row:
    return await AppealService.get_appeal(appeal_id, role_n_id)


@router.patch("/{appeal_id}", response_model=AppealResponse | None, summary="Update appeal")
async def update(
        appeal_id: int,
        user_upd_data: UserAppealUpdate = Depends(),
        executor_upd_data: ExecutorAppealUpdate = Depends(),
        role_n_id: tuple[UserRole, str] = Depends(allowed_for_all),
) -> Row | None:
    return await AppealService.update(appeal_id, user_upd_data, executor_upd_data, role_n_id)


@router.delete("/{appeal_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete appeal")
async def delete(appeal_id: int, role_n_id: tuple[UserRole, str] = Depends(allowed_for_admin_user)) -> None:
    return await AppealService.delete(appeal_id, role_n_id)


@router.patch(
    "/{appeal_id}/assign",
    response_model=AppealResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Assign a executor",
)
async def executor_assign(
        appeal_id: int,
        executor_id: str | None = None,
        role_n_id: tuple[UserRole, str] = Depends(allowed_for_admin_executor),
) -> Row:
    return await AppealService.executor_assign(appeal_id, executor_id, role_n_id)
