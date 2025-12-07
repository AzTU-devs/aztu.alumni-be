import random
from datetime import datetime
from app.models.auth import Auth
from app.core.session import get_db
from app.models.vacancy import Vacancy
from sqlalchemy import select, func, or_
from app.api.v1.schemas.vacancy import *
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.saved_vacancy import SavedVacancy
from fastapi import Depends, HTTPException, status
from app.models.vacancy_category import VacancyCategory
import json
from app.core.redis_client import get_redis

CURRENCY_MAP = {
    1: "AZN",
    2: "USD",
    3: "EUR"
}

EMPLOYMENT_TYPE_MAP = {
    1: "Tam ştat",
    2: "Yarım ştat",
    3: "Özünüməşğul",
    4: "Frilans",
    5: "Müqaviləli",
    6: "Təcrübəçi",
    7: "Könüllü"
}

JOB_LOCATION_TYPE_MAP = {
    1: "Ofisdə",
    2: "Hibrid",
    3: "Uzaqdan"
}
def generate_vacancy_code():
    random_number = random.randint(100000, 999999)
    return f"VACANCY-{random_number}"

async def create_vacancy(
    vacancy_request: VacancyCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        category_query = await db.execute(
            select(VacancyCategory)
            .where(VacancyCategory.category_code == vacancy_request.category_code)
        )

        category = category_query.scalar_one_or_none()

        if not category:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Category code is invalid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        vacancy_code = generate_vacancy_code()

        new_vacancy = Vacancy(
            vacancy_code=vacancy_code,
            category_code=vacancy_request.category_code,
            job_title=vacancy_request.job_title,
            company=vacancy_request.company,
            working_hours=vacancy_request.working_hours,
            job_location_type=vacancy_request.job_location_type,
            employment_type=vacancy_request.employment_type,
            country=vacancy_request.country,
            city=vacancy_request.city,
            salary_min=vacancy_request.salary_min,
            salary_max=vacancy_request.salary_max,
            currency=1,
            is_salary_public=vacancy_request.is_salary_public,
            deadline=vacancy_request.deadline,
            status=1,
            description=vacancy_request.description,
            html_content=vacancy_request.html_content,
            created_at=datetime.utcnow()
        )

        db.add(new_vacancy)
        await db.commit()
        await db.refresh(new_vacancy)

        # Reset vacancies cache
        redis_conn = await get_redis()
        keys = await redis_conn.keys("vacancies:*")
        if keys:
            await redis_conn.delete(*keys)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Vacancy created successfully."
            }, status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_vacancies(
    uuid: str | None = None,
    db: AsyncSession = Depends(get_db),
    start: int = 0,
    end: int = 10,
    search: str | None = None,
    employment_type: int | None = None,
    job_location_type: int | None = None,
    vacancy_category: str | None = None
):
    try:
        if end <= start or start < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="`start` must be >= 0 and `end` must be greater than `start`"
            )

        redis_conn = await get_redis()

        cache_key = f"vacancies:{uuid}:{start}:{end}:{search}:{employment_type}:{job_location_type}:{vacancy_category}"

        cached_data = await redis_conn.get(cache_key)

        if cached_data:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=json.loads(cached_data)
            )

        base_query = select(Vacancy)

        saved_codes = set()

        if uuid:
            saved_query = await db.execute(
                select(SavedVacancy.vacancy_code)
                .where(SavedVacancy.uuid == uuid)
            )
            saved_codes = set(saved_query.scalars().all())

        if search:
            normalized_search = search.lower().replace("-", "").replace(" ", "")

            base_query = base_query.where(
                or_(
                    func.replace(func.replace(func.lower(Vacancy.job_title), '-', ''), ' ', '').like(f"%{normalized_search}%"),
                    func.lower(Vacancy.company).like(f"%{search.lower()}%"),
                    func.lower(Vacancy.country).like(f"%{search.lower()}%"),
                    func.lower(Vacancy.city).like(f"%{search.lower()}%")
                )
            )

        if employment_type:
            base_query = base_query.where(Vacancy.employment_type == employment_type)

        if job_location_type:
            base_query = base_query.where(Vacancy.job_location_type == job_location_type)

        if vacancy_category:
            base_query = base_query.where(Vacancy.category_code == vacancy_category)

        total_query = await db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_query.scalar() or 0

        vacancy_query = await db.execute(
            base_query
            .offset(start)
            .limit(end - start)
        )

        vacancy_arr = []

        vacancies = vacancy_query.scalars().all()

        if not vacancies:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )

        for vacancy in vacancies:
            category_query = await db.execute(
                select(VacancyCategory)
                .where(VacancyCategory.category_code == vacancy.category_code)
            )

            category = category_query.scalar_one_or_none()

            vacancy_obj = {
                "vacancy_code": vacancy.vacancy_code,
                "category": category.title if category else None,
                "job_title": vacancy.job_title,
                "company": vacancy.company,
                "working_hours": vacancy.working_hours,
                "job_location_type": JOB_LOCATION_TYPE_MAP.get(vacancy.job_location_type, None),
                "employment_type": EMPLOYMENT_TYPE_MAP.get(vacancy.employment_type, None),
                "country": vacancy.country,
                "city": vacancy.city,
                "salary_min": vacancy.salary_min,
                "salary_max": vacancy.salary_max,
                "currency": CURRENCY_MAP.get(vacancy.currency, None),
                "is_salary_public": vacancy.is_salary_public,
                "deadline": vacancy.deadline.isoformat() if vacancy.deadline else None,
                "status": vacancy.status,
                "description": vacancy.description,
                "html_content": vacancy.html_content,
                "created_at": vacancy.created_at.isoformat() if vacancy.created_at else None,
                "is_saved": vacancy.vacancy_code in saved_codes,
            }

            vacancy_arr.append(vacancy_obj)
        
        response_payload = {
            "status_code": 200,
            "message": "Vacancies fetched successfully",
            "vacancy": vacancy_arr
        }

        await redis_conn.set(
            cache_key,
            json.dumps(response_payload, default=str)
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_payload
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def save_vacancy(
    request: SaveVacancy,
    db: AsyncSession = Depends(get_db)
):
    try:
        vacancy_query = await db.execute(
            select(Vacancy)
            .where(Vacancy.vacancy_code == request.vacancy_code)
        )

        vacancy = vacancy_query.scalar_one_or_none()

        if not vacancy:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Vacancy not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        user_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == request.uuid)
        )

        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "UUID is not valid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the vacancy is already saved
        saved_query = await db.execute(
            select(SavedVacancy)
            .where(SavedVacancy.uuid == request.uuid)
            .where(SavedVacancy.vacancy_code == request.vacancy_code)
        )

        saved_vacancy = saved_query.scalar_one_or_none()

        if saved_vacancy:
            # If already saved, unsave it
            await db.delete(saved_vacancy)
            await db.commit()
            message = "Vacancy unsaved successfully."
        else:
            # If not saved, save it
            new_saved_vacancy = SavedVacancy(
                uuid=request.uuid,
                vacancy_code=request.vacancy_code,
                created_at=datetime.utcnow()
            )
            db.add(new_saved_vacancy)
            await db.commit()
            await db.refresh(new_saved_vacancy)
            message = "Vacancy saved successfully."

        redis_conn = await get_redis()

        # Delete the saved vacancies cache
        saved_cache_key = f"saved_vacancies:{request.uuid}"
        await redis_conn.delete(saved_cache_key)

        # Delete all vacancies cache (so `is_saved` is updated)
        vacancies_keys = await redis_conn.keys("vacancies:*")
        if vacancies_keys:
            await redis_conn.delete(*vacancies_keys)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": message
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_saved_vacancies(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        redis_conn = await get_redis()
        cache_key = f"saved_vacancies:{uuid}"
        cached_data = await redis_conn.get(cache_key)
        if cached_data:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=json.loads(cached_data)
            )

        user_query = await db.execute(
            select(Auth).where(Auth.uuid == uuid)
        )
        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "UUID is not valid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        saved_vacancy_query = await db.execute(
            select(SavedVacancy).where(SavedVacancy.uuid == uuid)
        )
        saved_vacancies = saved_vacancy_query.scalars().all()

        if not saved_vacancies:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )

        vacancy_arr = []

        for saved_vacancy in saved_vacancies:

            vacancy_query = await db.execute(
                select(Vacancy).where(Vacancy.vacancy_code == saved_vacancy.vacancy_code)
            )
            vacancy = vacancy_query.scalar_one_or_none()

            vacancy_obj = {
                "vacancy_code": vacancy.vacancy_code,
                "job_title": vacancy.job_title,
                "company": vacancy.company,
                "working_hours": vacancy.working_hours,
                "job_location_type": JOB_LOCATION_TYPE_MAP.get(vacancy.job_location_type, None),
                "employment_type": EMPLOYMENT_TYPE_MAP.get(vacancy.employment_type, None),
                "country": vacancy.country,
                "city": vacancy.city,
                "salary_min": vacancy.salary_min,
                "salary_max": vacancy.salary_max,
                "currency": CURRENCY_MAP.get(vacancy.currency, None),
                "is_salary_public": vacancy.is_salary_public,
                "deadline": vacancy.deadline.isoformat() if vacancy.deadline else None,
                "status": vacancy.status,
                "description": vacancy.description,
                "html_content": vacancy.html_content,
                "created_at": vacancy.created_at.isoformat() if vacancy.created_at else None,
            }
            
            vacancy_arr.append(vacancy_obj)

        response_payload = {
            "status_code": 200,
            "message": "Saved vacancies fetched successfully.",
            "vacancies": vacancy_arr
        }

        # Cache the result in Redis
        await redis_conn.set(cache_key, json.dumps(response_payload, default=str))

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_payload
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )