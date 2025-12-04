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
    search: str | None = Query(default=None),
    employment_type: int | None = Query(default=None),
    job_location_type: int | None = Query(default=None),
    vacancy_category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    return await get_vacancies(
        start=start,
        end=end,
        search=search,
        employment_type=employment_type,
        job_location_type=job_location_type,
        vacancy_category=vacancy_category,
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