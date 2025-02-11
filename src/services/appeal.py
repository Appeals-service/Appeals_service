import asyncio

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row

from clients.S3 import s3_client
from common.settings import settings
from db.connector import AsyncSession
from dto.schemas.appeals import AppealCreate, AppealListFilters, ExecutorAppealUpdate, UserAppealUpdate
from repositories.appeal import AppealRepository
from utils.enums import AppealStatus, UserRole


class AppealService:

    @classmethod
    async def create(cls, appeal_data: AppealCreate, user_id: str) -> None:
        filenames_photo_dict = {}
        file_links = []
        if photo := appeal_data.photo:
            filenames_photo_dict, file_links = cls._get_photo_data(photo, user_id)

        appeal_data = appeal_data.model_dump(exclude={"photo"})
        appeal_data.update({"user_id": user_id, "status": AppealStatus.accepted, "photo": file_links})

        async with AsyncSession() as session:
            await AppealRepository.insert(session, appeal_data)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

        asyncio.create_task(s3_client.upload_files(filenames_photo_dict))

    @staticmethod
    async def get_appeals_list(filters: AppealListFilters, role_n_id: tuple[UserRole, str]) -> list[Row]:
        filters = filters.model_dump()

        if filters.get("self") and role_n_id[0] in {UserRole.user, UserRole.executor}:
            filters.update({f"{role_n_id[0]}_id": role_n_id[1]})

        async with AsyncSession() as session:
            return await AppealRepository.select_appeals_list(session, filters)


    @staticmethod
    async def get_appeal(appeal_id: int, role_n_id: tuple[UserRole, str]) -> Row:
        user_id = role_n_id[1] if role_n_id[0] == UserRole.user else None

        async with AsyncSession() as session:
            appeal_row = await AppealRepository.select_appeal(session, appeal_id, user_id)

        if not appeal_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal not found")

        return appeal_row

    @classmethod
    async def users_update(
            cls,
            appeal_id: int,
            user_upd_data: UserAppealUpdate,
            role_n_id: tuple[UserRole, str],
    ) -> Row | None:
        filters = {"id": appeal_id}
        if role_n_id[0] == UserRole.user:
            filters.update({"user_id": role_n_id[1], "status": AppealStatus.accepted})

        values = user_upd_data.model_dump(exclude_none=True, exclude={"photo"})

        filenames_photo_dict = {}
        if photo := user_upd_data.photo:
            filenames_photo_dict, file_links = cls._get_photo_data(photo, role_n_id[1])
            values.update({"photo": file_links})

        async with AsyncSession() as session:
            if photo:
                old_photo_links = await AppealRepository.select_appeals_photo(session, filters)
            appeal_row = await AppealRepository.update(session, filters, values)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

        if not appeal_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal for update not found")

        photo_to_delete = [link.split("/")[-1] for link in old_photo_links[0]]
        asyncio.create_task(s3_client.delete_files(photo_to_delete))
        asyncio.create_task(s3_client.upload_files(filenames_photo_dict))

        return appeal_row

    @classmethod
    async def executors_update(
            cls,
            appeal_id: int,
            executor_upd_data: ExecutorAppealUpdate,
            role_n_id: tuple[UserRole, str],
    ) -> Row | None:
        filters = {"id": appeal_id}
        if role_n_id[0] == UserRole.executor:
            filters.update({"executor_id": role_n_id[1], "status": AppealStatus.in_progress})

        if not (values := executor_upd_data.model_dump(exclude_none=True)):
            return

        async with AsyncSession() as session:
            appeal_row = await AppealRepository.update(session, filters, values)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

        if not appeal_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal for update not found")

        return appeal_row

    @staticmethod
    async def delete(appeal_id: int, role_n_id: tuple[UserRole, str]) -> None:
        filters = {"id": appeal_id}
        if role_n_id[0] == UserRole.user:
            filters.update({"user_id": role_n_id[1], "status": AppealStatus.accepted})

        async with AsyncSession() as session:
            await AppealRepository.delete(session, filters)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

    @staticmethod
    async def executor_assign(appeal_id: int, executor_id: str | None, role_n_id: tuple[UserRole, str]) -> Row:
        if role_n_id[0] == UserRole.admin and not executor_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The executor's ID is required")
        elif role_n_id[0] == UserRole.executor:
            executor_id = role_n_id[1]

        filters = {"id": appeal_id, "status": AppealStatus.accepted}
        values = {"executor_id": executor_id, "status": AppealStatus.in_progress}

        async with AsyncSession() as session:
            appeal_row = await AppealRepository.update(session, filters, values)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

        if not appeal_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal for assign not found")

        return appeal_row

    @classmethod
    def _get_photo_data(cls, photo_list: list[UploadFile], user_id: str) -> tuple[dict[str, bytes], list[str]]:
        filenames_photo_dict = {}
        file_links = []
        for photo in photo_list:
            filename = f"{user_id}_{photo.filename}"
            filenames_photo_dict[filename] = photo.file.read()
            file_links.append(f"{settings.SELECTEL_STORAGE_DOMAIN}/{filename}")

        return filenames_photo_dict, file_links
