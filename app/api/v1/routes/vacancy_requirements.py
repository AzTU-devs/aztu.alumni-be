from app.core.database import get_db
from fastapi import APIRouter, Depends
from app.util.limiter import create_limiter
from app.services.vacancy_requirements import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.util.jwt_required import token_required
from app.api.v1.schemas.vacancy_requirements import *

router = APIRouter()

@router.get("/{vacancy_code}")
async def get_requirements_by_code_endpoint(
    vacancy_code: str,
    user = Depends(token_required([1, 2, 3])),
    _ = create_limiter(times=10, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    return await get_requirements_by_code(
        vacacny_code=vacancy_code,
        db=db
    )

@router.post("/create")
async def create_requirement_endpoint(
    request: CreateRequiremt,
    user = Depends(token_required([2, 3])),
    _ = create_limiter(times=10, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    return await create_requirement(
        request=request,
        db=db
    )