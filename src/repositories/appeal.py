from sqlalchemy import insert

from db.connector import AsyncSession
from db.tables.appeals import Appeal


class AppealRepository:

    @classmethod
    async def insert_appeal(cls, session: AsyncSession, appeal_data: dict) -> None:
        query = insert(Appeal)