from app.core.database import get_db
from app.services.education import *
from app.api.v1.schemas.auth import *
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

router = APIRouter()

@router.get("/{uuid}")
async def get_education_by_uuid_endpoint(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    return await get_education_by_uuid(
        uuid=uuid,
        db=db
    )