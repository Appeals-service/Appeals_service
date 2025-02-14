from sqlalchemy import select, Select, update, delete, insert
from sqlalchemy.engine.row import Row

from datetime import timedelta

from src.db.connector import AsyncSession
from src.db.tables import Appeal


class AppealRepository:

    @staticmethod
    async def insert(session: AsyncSession, appeal_data: dict) -> int:
        query = insert(Appeal).values(**appeal_data).returning(Appeal.id)
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def select_appeals_list(cls, session: AsyncSession, filters: dict) -> list[Row]:
        query = select(
            Appeal.id, Appeal.message, Appeal.responsibility_area, Appeal.status, Appeal.comment, Appeal.created_at
        )
        query = cls._get_filtered_query(query, filters)
        result = await session.execute(query)
        return result.all()

    @staticmethod
    async def select_appeal(session: AsyncSession, appeal_id: int, user_id: str | None = None) -> Row:
        query = select(
            Appeal.id,
            Appeal.message,
            Appeal.photo,
            Appeal.responsibility_area,
            Appeal.status,
            Appeal.comment,
            Appeal.created_at,
        ).where(Appeal.id == appeal_id)

        if user_id:
            query = query.where(Appeal.user_id == user_id)

        result = await session.execute(query)
        return result.one_or_none()

    @staticmethod
    async def select_appeals_photo(session: AsyncSession, filters: dict) -> list:
        query = select(Appeal.photo).filter_by(**filters)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update(session: AsyncSession, filters: dict, values: dict) -> Row:
        query = update(Appeal).values(**values).filter_by(**filters).returning(
            Appeal.id,
            Appeal.user_id,
            Appeal.message,
            Appeal.photo,
            Appeal.responsibility_area,
            Appeal.status,
            Appeal.comment,
            Appeal.created_at,
        )
        result = await session.execute(query)
        return result.one_or_none()

    @staticmethod
    async def delete(session: AsyncSession, filters: dict) -> list:
        query = delete(Appeal).filter_by(**filters).returning(Appeal.photo)
        result = await session.execute(query)
        return result.scalars().all()

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

        return query.order_by(Appeal.id)