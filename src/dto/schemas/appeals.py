from datetime import datetime

from pydantic import BaseModel, Field

from utils.enums import AppealResponsibilityArea, AppealStatus


class BaseAppeal(BaseModel):
    message: str = Field(min_length=10, max_length=500, examples=["You really need to do something"])
    responsibility_area: AppealResponsibilityArea = Field(examples=[AppealResponsibilityArea.housing])


class AppealCreate(BaseAppeal):
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
    ...
