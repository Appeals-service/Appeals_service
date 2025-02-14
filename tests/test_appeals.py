import pytest
from sqlalchemy import select, insert
from fastapi import status
from random import choice

from src.db.connector import AsyncSession
from src.db.tables.appeals import Appeal
from src.utils.enums import AppealStatus, AppealResponsibilityArea


@pytest.mark.parametrize(
    "message, responsibility_area, expected_status, expected_instance_from_db",
    [
        ("test_create_message_1", AppealResponsibilityArea.housing, status.HTTP_201_CREATED, Appeal),
        ("test_create_message_2", AppealResponsibilityArea.road, status.HTTP_201_CREATED, Appeal),
        ("test_create_message_3", AppealResponsibilityArea.administration, status.HTTP_201_CREATED, Appeal),
    ]
)
async def test_create(
        client, user_data, message, responsibility_area, expected_status, expected_instance_from_db
):
    params = {"message": message, "responsibility_area": responsibility_area}

    response = client.post("/api/v1/appeals/", params=params, cookies={"access_token": user_data.get("access_token")})
    async with AsyncSession() as session:
        result = await session.execute(select(Appeal).where(
            Appeal.user_id == user_data.get("user_id"),
            Appeal.message == message,
            Appeal.responsibility_area == responsibility_area,
            Appeal.status == AppealStatus.accepted,
        ))
        result = result.scalar()

    assert response.status_code == expected_status
    assert response.json() is None
    assert isinstance(result, expected_instance_from_db)


@pytest.mark.parametrize(
    "count, message, expected_status",
    [
        (1, "test_get_appeals_list", status.HTTP_200_OK),
        (2, "test_get_appeals_list", status.HTTP_200_OK),
        (3, "test_get_appeals_list", status.HTTP_200_OK),
    ]
)
async def test_get_appeals_list(client, user_data, count, message, expected_status):
    all_areas = [value for value in AppealResponsibilityArea]
    messages = [f"{message}_{i}" for i in range(count)]
    areas = [choice(all_areas) for _ in range(count)]
    values = []
    for msg, area in zip(messages, areas):
        values.append({
            "user_id": user_data.get("user_id"),
            "message": msg,
            "responsibility_area": area,
            "status": AppealStatus.accepted,
        })
    async with AsyncSession() as session:
        result = await session.execute(insert(Appeal).values(values).returning(Appeal.id))
        await session.commit()
        result = result.scalars().all()
    params = {"status": AppealStatus.accepted, "self": True}

    response = client.get("/api/v1/appeals/", params=params, cookies={"access_token": user_data.get("access_token")})
    response_json = response.json()

    assert response.status_code == expected_status
    assert len(response_json) == count
    assert [item.get("id") for item in response_json] == result
    assert [item.get("message") for item in response_json] == messages
    assert [item.get("responsibility_area") for item in response_json] == areas



@pytest.mark.parametrize(
    "message, responsibility_area, expected_status",
    [
        ("test_get_appeal_1", AppealResponsibilityArea.housing, status.HTTP_200_OK),
        ("test_get_appeal_2", AppealResponsibilityArea.law_enforcement, status.HTTP_200_OK),
        ("test_get_appeal_3", AppealResponsibilityArea.other, status.HTTP_200_OK),
    ]
)
async def test_get_appeal(client, user_data, message, responsibility_area, expected_status):
    values = {
        "user_id": user_data.get("user_id"),
        "message": message,
        "responsibility_area": responsibility_area,
        "status": AppealStatus.accepted,
    }
    async with AsyncSession() as session:
        result = await session.execute(insert(Appeal).values(values).returning(Appeal.id))
        await session.commit()
        result = result.scalar()
    response = client.get(f"/api/v1/appeals/{result}", cookies={"access_token": user_data.get("access_token")})
    response_json = response.json()
    print(response_json)

    assert response.status_code == expected_status
    assert response_json.get("id") == result
    assert response_json.get("message") == message
    assert response_json.get("responsibility_area") == responsibility_area

