from db.connector import AsyncSession
from dto.schemas.appeals import AppealCreate
from repositories.appeal import AppealRepository


class AppealService:

    @classmethod
    async def create_appeal(cls, appeal_data: AppealCreate, user_id: str):
        pass
        # async with AsyncSession() as session:
        #     await AppealRepository.insert_appeal(session, appeal_data)
