from app.core.database import get_db
from fastapi import APIRouter, Depends, Query
from app.services.vacancy_requirements import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.vacancy_requirements import *

router = APIRouter()

@router.get("/{vacancy_code}")
async def get_requirements_by_code_endpoint(
    vacancy_code: str,
    db: AsyncSession = Depends(get_db)
):
    return await get_requirements_by_code(
        vacacny_code=vacancy_code,
        db=db
    )

@router.post("/create")
async def create_requirement_endpoint(
    request: CreateRequiremt,
    db: AsyncSession = Depends(get_db)
):
    return await create_requirement(
        request=request,
        db=db
    )