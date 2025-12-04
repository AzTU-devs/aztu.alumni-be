from app.core.database import get_db
from fastapi import APIRouter, Depends
from app.services.work_experience import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.work_experience import *

router = APIRouter()

@router.get("/{uuid}")
async def get_experience_by_uuid_endpoint(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    return await get_experience_by_uuid(
        uuid=uuid,
        db=db
    )

@router.post("/create")
async def create_experience_endpoint(
    experience_request: CreateExperience,
    db: AsyncSession = Depends(get_db)
):
    return await create_experience(
        request=experience_request,
        db=db
    )