from sqladmin import ModelView

from db.tables import Appeal


class AppealAdmin(ModelView, model=Appeal):
    column_list = [column.name for column in Appeal.__table__.columns]
