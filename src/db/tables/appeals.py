from sqlalchemy import Column, Text, ARRAY, String, Enum, UUID

from src.db.tables.base import BaseModel, IdMixin, CreatedAtMixin, UpdatedAtMixin
from src.utils.enums import AppealStatus, AppealResponsibilityArea


class Appeals(BaseModel, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "appeals"

    user = Column(UUID, nullable=False, comment="User")
    message = Column(Text, nullable=False, comment="Appeals text")
    photo = Column(ARRAY(String), nullable=True, comment="Appeals photo")
    responsibility_area = Column(Enum(AppealResponsibilityArea), nullable=False, comment="Appeal responsibility area")
    executor =Column(UUID, nullable=True, comment="Executor")
    status = Column(Enum(AppealStatus), nullable=False, comment="Appeal status")
    comment = Column(Text, nullable=True, comment="Comment from executor")
