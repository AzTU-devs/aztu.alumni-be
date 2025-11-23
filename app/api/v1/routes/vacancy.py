from app.services.vacancy import *
from app.core.database import get_db
from app.api.v1.schemas.vacancy import *
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/all")
async def get_vacancies_endpoint(
    start: int = Query(ge=0),
    end: int = Query(ge=10),
    db: AsyncSession = Depends(get_db)
):
    return await get_vacancies(
        start=start,
        end=end,
        db=db
    )

@router.post("/create")
async def create_vacancy_endpoint(
    vacancy_request: VacancyCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_vacancy(
        vacancy_request=vacancy_request,
        db=db
    )