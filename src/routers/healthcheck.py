import asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db.connector import AsyncSession

router = APIRouter(tags=["healthcheck"])

RESPONSE = {
    200: {"content": {"application/json": {"example": {"healthcheck": "ok"}}}},
    500: {"content": {"application/json": {"example": {"healthcheck": "false", "error": "string"}}}},
}

@router.get("/healthcheck", responses=RESPONSE)
async def healthcheck() -> JSONResponse:
    """Service health check.

    Returning OK status after 1 sec awaiting if everything is good, else returning an error.
    """
    await asyncio.sleep(1)
    try:
        async with AsyncSession() as db_session:
            await db_session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return JSONResponse(content={"healthcheck": "false", "error": str(exc)}, status_code=500)
    return JSONResponse(content={"healthcheck": "ok"}, status_code=200)


@router.get("/healthcheck_app", responses=RESPONSE)
async def healthcheck_app() -> JSONResponse:
    """Service health check."""
    await asyncio.sleep(1)
    return JSONResponse(content={"healthcheck": "ok"}, status_code=status.HTTP_200_OK)
