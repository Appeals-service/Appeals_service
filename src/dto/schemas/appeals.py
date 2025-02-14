from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from fastapi import UploadFile, File

from src.utils.enums import AppealResponsibilityArea, AppealStatus
from src.common.settings import settings


class PhotoMixin:
    photo: list[UploadFile] | None = File(default=None, max_length=3)

    @field_validator("photo")
    @classmethod
    def check_photo(cls, photo_list: list[UploadFile]):
        if photo_list is None:
            return

        for photo in photo_list:
            if photo.size > settings.MAX_PHOTO_SIZE_IN_BYTES:
                raise ValueError("The maximum photo size has been exceeded")
            if not photo.headers.get("content-type").startswith("image/"):
                raise ValueError("Incorrect file uploaded")

        return photo_list


class BaseAppeal(BaseModel):
    message: str = Field(min_length=10, max_length=500, examples=["You really need to do something"])
    responsibility_area: AppealResponsibilityArea = Field(examples=[AppealResponsibilityArea.housing])


class AppealCreate(BaseAppeal, PhotoMixin):
    ...


class BaseFilters(BaseModel):
    limit: int | None = Field(default=None, gt=0, examples=[100])
    offset: int | None = Field(default=None, ge=0, examples=[0])


class AppealListFilters(BaseFilters):
    status: AppealStatus | None = Field(default=None, examples=[AppealStatus.accepted])
    responsibility_area: AppealResponsibilityArea | None = Field(
        default=None, examples=[AppealResponsibilityArea.housing]
    )
    created_date_from: datetime | None = Field(default=None, examples=["2025-01-01"])
    created_date_to: datetime | None = Field(default=None, examples=["2025-12-31"])
    self: bool | None = Field(default=True, description="Select only your own appeals")


class BaseAppealResponse(BaseAppeal):
    status: AppealStatus
    comment: str | None
    created_at: datetime
    id: int


class AppealListResponse(BaseAppealResponse):
    ...


class AppealResponse(BaseAppealResponse):
    photo: list[str] | None = None


class UserAppealUpdate(BaseModel, PhotoMixin):
    message: str | None = Field(
        default=None, min_length=10, max_length=500, examples=["You really need to do something"]
    )
    responsibility_area: AppealResponsibilityArea | None= Field(
        default=None, examples=[AppealResponsibilityArea.housing]
    )


class ExecutorAppealUpdate(BaseModel):
    status: AppealStatus | None = Field(default=None, examples=[AppealStatus.accepted])
    comment: str | None = Field(default=None, min_length=10, max_length=500, examples=["All done"])