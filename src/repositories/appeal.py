from sqlalchemy import select, Select

from datetime import timedelta

from db.connector import AsyncSession
from db.tables import Appeal


class AppealRepository:

    @classmethod
    async def insert_appeal(cls, session: AsyncSession, appeal_data: dict) -> None:
        session.add(Appeal(**appeal_data))

    @classmethod
    async def select_appeals_list(cls, session: AsyncSession, filters: dict) -> list[Appeal]:
        query = select(Appeal.message, Appeal.responsibility_area, Appeal.status, Appeal.comment, Appeal.created_at)
        query = cls._get_filtered_query(query, filters)
        appeals = await session.execute(query)
        return appeals.all()

    @staticmethod
    def _get_filtered_query(query: Select, filters: dict) -> Select:

        if user_id := filters.get("user_id"):
            query = query.where(Appeal.user_id == user_id)
        elif executor_id := filters.get("executor_id"):
            query = query.where(Appeal.executor_id == executor_id)

        if status := filters.get("status"):
            query = query.where(Appeal.status == status)
        if responsibility_area := filters.get("responsibility_area"):
            query = query.where(Appeal.responsibility_area == responsibility_area)
        if created_date_from := filters.get("created_date_from"):
            query = query.where(Appeal.created_at >= created_date_from)
        if created_date_to := filters.get("created_date_to"):
            query = query.where(Appeal.created_at <= created_date_to + timedelta(1))
        if limit := filters.get("limit"):
            query = query.limit(limit)
        if offset := filters.get("offset"):
            query = query.offset(offset)

        return query