from fastapi import APIRouter, status, Depends

from dto.schemas.appeals import AppealCreate, AppealListFilters, AppealListResponse, AppealResponse
from services.appeal import AppealService
from src.utils.role_checker import allowed_for_user, allowed_for_all
from utils.enums import UserRole

router = APIRouter(tags=["Appeal"])


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create appeal")
async def create_appeal(appeal_data: AppealCreate = Depends(), role_n_id: tuple[UserRole, str] = Depends(allowed_for_user)):
    return await AppealService.create_appeal(appeal_data, role_n_id[1])


@router.get("/", response_model=list[AppealListResponse], summary="Get appeals list")
async def get_appeals_list(
        filters: AppealListFilters = Depends(), role_n_id: tuple[UserRole, str] = Depends(allowed_for_all)
):
    return await AppealService.get_appeals_list(filters, role_n_id)


@router.get("/{appeal_id}", response_model=AppealResponse, summary="Get appeal detail")
async def get_appeal(appeal_id: int, role_n_id: tuple[UserRole, str] = Depends(allowed_for_all)):
    return await AppealService.get_appeal(appeal_id, role_n_id)

