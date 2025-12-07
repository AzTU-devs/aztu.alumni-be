from app.services.vacancy import *
from app.core.database import get_db
from app.api.v1.schemas.vacancy import *
from app.util.limiter import create_limiter
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.util.jwt_required import token_required
from app.util.current_user_dependency import get_current_user

router = APIRouter()

@router.get("/all")
async def get_vacancies_endpoint(
    uuid: str | None = None,
    start: int = Query(ge=0),
    end: int = Query(ge=10),
    search: str | None = Query(default=None),
    employment_type: int | None = Query(default=None),
    job_location_type: int | None = Query(default=None),
    vacancy_category: str | None = Query(default=None),
    _ = create_limiter(times=20, seconds=60),
    user = Depends(token_required([1, 2, 3])),
    db: AsyncSession = Depends(get_db)
):
    return await get_vacancies(
        uuid=uuid,
        start=start,
        end=end,
        search=search,
        employment_type=employment_type,
        job_location_type=job_location_type,
        vacancy_category=vacancy_category,
        db=db
    )

@router.get("/{uuid}/saved")
async def get_saved_vacancies_endpoint(
    uuid: str,
    current_user: dict = Depends(get_current_user),
    user = Depends(token_required([1, 2, 3])),
    _ = create_limiter(times=20, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )
    
    return await get_saved_vacancies(
        uuid=uuid,
        db=db
    )

@router.post("/save")
async def save_vacancy_endpoint(
    request: SaveVacancy,
    current_user: dict = Depends(get_current_user),
    user = Depends(token_required([1, 2, 3])),
    _ = create_limiter(times=10, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != request.uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )
    
    return await save_vacancy(
        request=request,
        db=db
    )

@router.post("/create")
async def create_vacancy_endpoint(
    vacancy_request: VacancyCreate,
    _ = create_limiter(times=10, seconds=60),
    user = Depends(token_required([2, 3])),
    db: AsyncSession = Depends(get_db)
):
    return await create_vacancy(
        vacancy_request=vacancy_request,
        db=db
    )
