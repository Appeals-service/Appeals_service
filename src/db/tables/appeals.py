from sqlalchemy import Column, Text, ARRAY, String, Enum, UUID

from db.tables.base import BaseModel, IdMixin, CreatedAtMixin, UpdatedAtMixin
from utils.enums import AppealStatus, AppealResponsibilityArea


class Appeal(BaseModel, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "appeals"

    user_id = Column(UUID, nullable=False, comment="User")
    message = Column(Text, nullable=False, comment="Appeal text")
    photo = Column(ARRAY(String), nullable=True, comment="Appeal photo")
    responsibility_area = Column(Enum(AppealResponsibilityArea), nullable=False, comment="Appeal responsibility area")
    executor_id =Column(UUID, nullable=True, comment="Executor")
    status = Column(Enum(AppealStatus), nullable=False, comment="Appeal status")
    comment = Column(Text, nullable=True, comment="Comment from executor")
