from app.core.database import get_db
from app.services.education import *
from app.api.v1.schemas.auth import *
from fastapi import APIRouter, Depends
from app.api.v1.schemas.education import *
from sqlalchemy.ext.asyncio import AsyncSession

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

@router.post("/create")
async def create_education_endpoint(
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db)
):
    return await create_education(
        education_request=education_request,
        db=db
    )