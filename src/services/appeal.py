import asyncio

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row

from src.clients.S3 import s3_client
from src.clients.broker.rabbitmq import rmq_client
from src.clients.http.authorization import authorization_client
from src.common.settings import settings
from src.db.connector import AsyncSession
from src.dto.schemas.appeals import AppealCreate, AppealListFilters, ExecutorAppealUpdate, UserAppealUpdate
from src.dto.schemas.users import JWTUserData
from src.repositories.appeal import AppealRepository
from src.utils.enums import AppealStatus, UserRole, LogLevel
from src.utils.logging import send_log


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
            appeal_id = await AppealRepository.insert(session, appeal_data)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

        if not settings.IS_TESTING:
            asyncio.create_task(s3_client.upload_files(filenames_photo_dict))
            await send_log(LogLevel.info, f"Appeal created. Appeal id = {appeal_id}. User id = {user_id}")

    @staticmethod
    async def get_appeals_list(filters: AppealListFilters, user_data: JWTUserData) -> list[Row]:
        filters = filters.model_dump()

        if filters.get("self") and user_data.role in {UserRole.user, UserRole.executor}:
            filters.update({f"{user_data.role}_id": user_data.id})

        async with AsyncSession() as session:
            return await AppealRepository.select_appeals_list(session, filters)


    @staticmethod
    async def get_appeal(appeal_id: int, user_data: JWTUserData) -> Row:
        user_id = user_data.id if user_data.role == UserRole.user else None

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
            user_data: JWTUserData,
    ) -> Row | None:
        filters = {"id": appeal_id}
        if user_data.role == UserRole.user:
            filters.update({"user_id": user_data.id, "status": AppealStatus.accepted})

        values = user_upd_data.model_dump(exclude_none=True, exclude={"photo"})

        filenames_photo_dict = {}
        if photo := user_upd_data.photo:
            filenames_photo_dict, file_links = cls._get_photo_data(photo, user_data.id)
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

        if not settings.IS_TESTING:
            if photo:
                photo_to_delete = [link.split("/")[-1] for link in old_photo_links[0]]
                asyncio.create_task(s3_client.delete_files(photo_to_delete))
                asyncio.create_task(s3_client.upload_files(filenames_photo_dict))

            await send_log(LogLevel.info, f"Appeal updated by user. Appeal id = {appeal_id}. User id = {user_data.id}")

        return appeal_row

    @classmethod
    async def executors_update(
            cls,
            appeal_id: int,
            executor_upd_data: ExecutorAppealUpdate,
            user_data: JWTUserData,
    ) -> Row | None:
        filters = {"id": appeal_id}
        if user_data.role == UserRole.executor:
            filters.update({"executor_id": user_data.id, "status": AppealStatus.in_progress})

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

        if not settings.IS_TESTING:
            await cls._send_notification(
                appeal_row.user_id, appeal_row.id, executor_upd_data.status, executor_upd_data.comment
            )
            await send_log(
                LogLevel.info, f"Appeal updated by executor. Appeal id = {appeal_id}. Executor id = {user_data.id}"
            )

        return appeal_row

    @staticmethod
    async def delete(appeal_id: int, user_data: JWTUserData) -> None:
        filters = {"id": appeal_id}
        if user_data.role == UserRole.user:
            filters.update({"user_id": user_data.id, "status": AppealStatus.accepted})

        async with AsyncSession() as session:
            photo_links = await AppealRepository.delete(session, filters)
            try:
                await session.commit()
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args[0].split('DETAIL:')[1]}")

        if not settings.IS_TESTING:
            if photo_links := photo_links[0]:
                photo_to_delete = [link.split("/")[-1] for link in photo_links]
                asyncio.create_task(s3_client.delete_files(photo_to_delete))

            await send_log(LogLevel.info, f"Appeal deleted. Appeal id = {appeal_id}. User id = {user_data.id}")


    @staticmethod
    async def executor_assign(appeal_id: int, executor_id: str | None, user_data: JWTUserData) -> Row:
        if user_data.role == UserRole.admin and not executor_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The executor's ID is required")
        elif user_data.role == UserRole.executor:
            executor_id = user_data.id

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

        if not settings.IS_TESTING:
            await send_log(
                LogLevel.info,
                f"Appeal is assigned to the executor. Appeal id = {appeal_id}. Executor id = {executor_id}",
            )

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

    @classmethod
    async def _get_user_email(cls, user_id: str) -> str:
        response_status, response = await authorization_client.get_user_email(user_id)

        if response_status != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response)

        if not response:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is no email")

        return response

    @classmethod
    async def _send_notification(cls, user_id: str, appeal_id: str, appeal_status: AppealStatus, comment: str) -> None:
        user_email = await cls._get_user_email(user_id)
        message = {"email": user_email.strip('"'), "appeal_id": appeal_id, "status": appeal_status, "comment": comment}
        await rmq_client.send_notification(message)
