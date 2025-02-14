import pytest
from sqlalchemy import select
from fastapi import status

from src.db.connector import AsyncSession
from src.db.tables.appeals import Appeal
from src.utils.enums import AppealStatus, AppealResponsibilityArea


@pytest.mark.parametrize(
    "message, responsibility_area, expected_status, instance_expected_from_db",
    [
        ("test_create_message_1", AppealResponsibilityArea.housing, status.HTTP_201_CREATED, Appeal),
        ("test_create_message_2", AppealResponsibilityArea.road, status.HTTP_201_CREATED, Appeal),
        ("test_create_message_3", AppealResponsibilityArea.administration, status.HTTP_201_CREATED, Appeal),
    ]
)
async def test_create(
        client, user_access_token, message, responsibility_area, expected_status, instance_expected_from_db
):
    params = {"message": message, "responsibility_area": responsibility_area}

    response = client.post("/api/v1/appeals/", params=params, cookies={"access_token": user_access_token})
    async with AsyncSession() as session:
        result = await session.execute(select(Appeal).where(
            Appeal.message == message,
            Appeal.responsibility_area == responsibility_area,
            Appeal.status == AppealStatus.accepted,
        ))
        result = result.scalar()

    assert response.status_code == expected_status
    assert response.json() is None
    assert isinstance(result, instance_expected_from_db)

