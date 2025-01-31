from fastapi import APIRouter, status


router = APIRouter(tags=["Appeals"])


@router.post("/",status_code=status.HTTP_201_CREATED, summary="Create appeal")
async def create_appeal(msg: str):
    return msg
