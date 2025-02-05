from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row

from db.connector import AsyncSession
from db.tables import Appeal
from dto.schemas.appeals import AppealCreate, AppealListFilters
from repositories.appeal import AppealRepository
from utils.enums import AppealStatus, UserRole


class AppealService:

    @classmethod
    async def create_appeal(cls, appeal_data: AppealCreate, user_id: str):
        appeal_data = appeal_data.model_dump()
        appeal_data.update({"user_id": user_id, "status": AppealStatus.accepted})

        async with AsyncSession() as session:
            await AppealRepository.insert_appeal(session, appeal_data)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

    @classmethod
    async def get_appeals_list(cls, filters: AppealListFilters, role_n_id: tuple[UserRole, str]) -> list[Row]:
        filters = filters.model_dump()

        if filters.get("self") and role_n_id[0] in {UserRole.user, UserRole.executor}:
            filters.update({f"{role_n_id[0]}_id": role_n_id[1]})

        async with AsyncSession() as session:
            return await AppealRepository.select_appeals_list(session, filters)


    @classmethod
    async def get_appeal(cls, appeal_id: int, role_n_id: tuple[UserRole, str]) -> Row:
        user_id = role_n_id[1] if role_n_id[0] == UserRole.user else None

        async with AsyncSession() as session:
            appeal = await AppealRepository.select_appeal(session, appeal_id, user_id)

        if not appeal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal not found")

        return appeal
