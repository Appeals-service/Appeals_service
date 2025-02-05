from fastapi import APIRouter, status, Depends

from dto.schemas.appeals import AppealCreate
from services.appeal import AppealService
from src.utils.role_checker import allowed_for_user

router = APIRouter(tags=["Appeal"])


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create appeal")
async def create_appeal(appeal_data: AppealCreate = Depends(), user_id: str = Depends(allowed_for_user)):
    return await AppealService.create_appeal(appeal_data, user_id)
