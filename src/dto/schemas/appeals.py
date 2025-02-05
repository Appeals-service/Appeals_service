from pydantic import BaseModel, Field

from utils.enums import AppealResponsibilityArea


class AppealCreate(BaseModel):
    msg: str = Field(min_length=10, max_length=500, examples=["You really need to do something"])
    responsibility_area: AppealResponsibilityArea = Field(examples=[AppealResponsibilityArea.housing])
