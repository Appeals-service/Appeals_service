from fastapi import APIRouter
from src.routers.v1.sending_api import router as sending_api_router
from src.routers.v1.appeals import router as appeals_router


router = APIRouter(prefix="/api/v1")

router.include_router(sending_api_router)
router.include_router(appeals_router)
