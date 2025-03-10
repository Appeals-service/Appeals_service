from random import choice
from uuid import uuid4

import pytest
from fastapi import status
from sqlalchemy import insert, select

from db.connector import AsyncSession
from db.tables.appeals import Appeal
from utils.enums import AppealResponsibilityArea, AppealStatus


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
            Appeal.user_id == user_data.get("id"),
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
        (1, "test_get_appeals_list_message", status.HTTP_200_OK),
        (2, "test_get_appeals_list_message", status.HTTP_200_OK),
        (3, "test_get_appeals_list_message", status.HTTP_200_OK),
    ]
)
async def test_get_appeals_list(client, user_data, count, message, expected_status):
    all_areas = [value for value in AppealResponsibilityArea]
    messages = [f"{message}_{i}" for i in range(count)]
    areas = [choice(all_areas) for _ in range(count)]
    values = []
    for msg, area in zip(messages, areas):
        values.append({
            "user_id": user_data.get("id"),
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
        ("test_get_appeal_message_1", AppealResponsibilityArea.housing, status.HTTP_200_OK),
        ("test_get_appeal_message_2", AppealResponsibilityArea.law_enforcement, status.HTTP_200_OK),
        ("test_get_appeal_message_3", AppealResponsibilityArea.other, status.HTTP_200_OK),
    ]
)
async def test_get_appeal(client, user_data, message, responsibility_area, expected_status):
    values = {
        "user_id": user_data.get("id"),
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

    assert response.status_code == expected_status
    assert response_json.get("id") == result
    assert response_json.get("message") == message
    assert response_json.get("responsibility_area") == responsibility_area


@pytest.mark.parametrize(
    "message, responsibility_area, expected_status, new_message, new_responsibility_area",
    [
        (
                "test_users_update_message_1",
                AppealResponsibilityArea.housing,
                status.HTTP_200_OK,
                "test_users_update_new_message_1",
                AppealResponsibilityArea.other,
        ),
        (
                "test_users_update_message_2",
                AppealResponsibilityArea.law_enforcement,
                status.HTTP_200_OK,
                "test_users_update_new_message_2",
                AppealResponsibilityArea.road,
        ),
        (
                "test_users_update_message_3",
                AppealResponsibilityArea.other,
                status.HTTP_200_OK,
                "test_users_update_new_message_3",
                AppealResponsibilityArea.administration,
        ),
    ]
)
async def test_users_update(
        client, user_data, message, responsibility_area, expected_status, new_message, new_responsibility_area
):
    values = {
        "user_id": user_data.get("id"),
        "message": message,
        "responsibility_area": responsibility_area,
        "status": AppealStatus.accepted,
    }
    async with AsyncSession() as session:
        insert_result = await session.execute(insert(Appeal).values(values).returning(Appeal.id))
        await session.commit()
        insert_result = insert_result.scalar()
    params = {"message": new_message, "responsibility_area": new_responsibility_area}

    response = client.patch(
        f"/api/v1/appeals/{insert_result}/user",
        params=params,
        cookies={"access_token": user_data.get("access_token")},
    )
    response_json = response.json()
    async with AsyncSession() as session:
        select_result = await session.execute(select(Appeal).where(Appeal.id == insert_result))
        select_result = select_result.scalar()

    assert response.status_code == expected_status
    assert response_json.get("id") == insert_result
    assert response_json.get("message") == new_message == select_result.message
    assert response_json.get("responsibility_area") == new_responsibility_area == select_result.responsibility_area


@pytest.mark.parametrize(
    "message, responsibility_area, expected_status, new_appeal_status, comment",
    [
        (
                "test_executors_update_message_1",
                AppealResponsibilityArea.road,
                status.HTTP_200_OK,
                AppealStatus.done,
                "test_executors_update_comment_3",
        ),
        (
                "test_executors_update_message_2",
                AppealResponsibilityArea.law_enforcement,
                status.HTTP_200_OK,
                AppealStatus.cancelled,
                "test_executors_update_comment_3",
        ),
        (
                "test_executors_update_message_3",
                AppealResponsibilityArea.administration,
                status.HTTP_200_OK,
                AppealStatus.done,
                "test_executors_update_comment_3",
        ),
    ]
)
async def test_executors_update(
        client, executor_data, message, responsibility_area, expected_status, new_appeal_status, comment
):
    values = {
        "user_id": str(uuid4()),
        "message": message,
        "responsibility_area": responsibility_area,
        "executor_id": executor_data.get("id"),
        "status": AppealStatus.in_progress,
    }
    async with AsyncSession() as session:
        insert_result = await session.execute(insert(Appeal).values(values).returning(Appeal.id))
        await session.commit()
        insert_result = insert_result.scalar()
    params = {"status": new_appeal_status, "comment": comment}

    response = client.patch(
        f"/api/v1/appeals/{insert_result}/executor",
        params=params,
        cookies={"access_token": executor_data.get("access_token")},
    )
    response_json = response.json()
    async with AsyncSession() as session:
        select_result = await session.execute(select(Appeal).where(Appeal.id == insert_result))
        select_result = select_result.scalar()

    assert response.status_code == expected_status
    assert response_json.get("id") == insert_result
    assert response_json.get("status") == new_appeal_status == select_result.status
    assert response_json.get("comment") == comment == select_result.comment


@pytest.mark.parametrize(
    "message, responsibility_area, expected_status",
    [
        ("test_delete_message_1", AppealResponsibilityArea.housing, status.HTTP_204_NO_CONTENT),
        ("test_delete_message_2", AppealResponsibilityArea.law_enforcement, status.HTTP_204_NO_CONTENT),
        ("test_delete_message_3", AppealResponsibilityArea.other, status.HTTP_204_NO_CONTENT),
    ]
)
async def test_delete(client, user_data, message, responsibility_area, expected_status):
    values = {
        "user_id": user_data.get("id"),
        "message": message,
        "responsibility_area": responsibility_area,
        "status": AppealStatus.accepted,
    }
    async with AsyncSession() as session:
        insert_result = await session.execute(insert(Appeal).values(values).returning(Appeal.id))
        await session.commit()
        insert_result = insert_result.scalar()

    response = client.delete(
        f"/api/v1/appeals/{insert_result}", cookies={"access_token": user_data.get("access_token")}
    )
    async with AsyncSession() as session:
        select_result = await session.execute(select(Appeal).where(Appeal.id == insert_result))
        select_result = select_result.scalar()

    assert response.status_code == expected_status
    assert select_result is None


@pytest.mark.parametrize(
    "message, responsibility_area, expected_status, new_appeal_status",
    [
        (
                "test_executor_assign_message_1",
                AppealResponsibilityArea.road,
                status.HTTP_202_ACCEPTED,
                AppealStatus.in_progress,
        ),
        (
                "test_executor_assign_message_2",
                AppealResponsibilityArea.administration,
                status.HTTP_202_ACCEPTED,
                AppealStatus.in_progress,
        ),
        (
                "test_executor_assign_message_3",
                AppealResponsibilityArea.housing,
                status.HTTP_202_ACCEPTED,
                AppealStatus.in_progress,
        ),
    ]
)
async def test_executor_assign(
        client, executor_data, message, responsibility_area, expected_status, new_appeal_status
):
    values = {
        "user_id": str(uuid4()),
        "message": message,
        "responsibility_area": responsibility_area,
        "status": AppealStatus.accepted,
    }
    async with AsyncSession() as session:
        insert_result = await session.execute(insert(Appeal).values(values).returning(Appeal.id))
        await session.commit()
        insert_result = insert_result.scalar()

    response = client.patch(
        f"/api/v1/appeals/{insert_result}/assign", cookies={"access_token": executor_data.get("access_token")}
    )
    response_json = response.json()
    async with AsyncSession() as session:
        select_result = await session.execute(select(Appeal).where(Appeal.id == insert_result))
        select_result = select_result.scalar()

    assert response.status_code == expected_status
    assert response_json.get("id") == insert_result
    assert str(select_result.executor_id) == executor_data.get("id")
    assert response_json.get("status") == new_appeal_status == select_result.status
