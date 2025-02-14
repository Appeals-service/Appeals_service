from fastapi.testclient import TestClient
from asyncio import get_event_loop
import pytest
from alembic import command
from alembic.config import Config

from sqlalchemy import text
from src.common.settings import ROOT_DIR, settings
from src.db.connector import AsyncSession
from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def apply_migrations():
    assert settings.TEST_DATABASE_SCHEMA_PREFIX in settings.SCHEMA, "Попытка использовать не тестовую схему."

    alembic_cfg = Config(str(ROOT_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(ROOT_DIR / "migrations"))

    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")

    async with AsyncSession() as session:
        await session.execute(text(f"DROP SCHEMA IF EXISTS {settings.SCHEMA} CASCADE;"))
        await session.commit()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
