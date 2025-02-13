from fastapi import APIRouter
from src.routers.v1.appeals import router as appeals_router
from src.routers.v1.users import router as users_router


router = APIRouter(prefix="/api/v1")

router.include_router(appeals_router)
router.include_router(users_router)
