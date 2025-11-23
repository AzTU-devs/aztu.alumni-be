import random
from datetime import datetime
from sqlalchemy import select, func
from app.core.session import get_db
from app.models.vacancy import Vacancy, JobLocationType, EmploymentType, VacancyStatus, Currency
from app.api.v1.schemas.vacancy import *
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.models.vacancy_category import VacancyCategory

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
            job_location_type=JobLocationType[vacancy_request.job_location_type].value,
            employment_type=EmploymentType[vacancy_request.employment_type].value,
            country=vacancy_request.country,
            city=vacancy_request.city,
            salary_min=vacancy_request.salary_min,
            salary_max=vacancy_request.salary_max,
            currency=Currency[vacancy_request.currency].value,
            is_salary_public=vacancy_request.is_salary_public,
            deadline=vacancy_request.deadline,
            status=VacancyStatus[vacancy_request.status].value,
            created_at=datetime.utcnow()
        )

        db.add(new_vacancy)
        await db.commit()
        await db.refresh(new_vacancy)

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
            }
        )

async def get_vacancies(
    db: AsyncSession = Depends(get_db),
    start: int = 0,
    end: int = 10
):
    try:
        if end <= start or start < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="`start` must be >= 0 and `end` must be greater than `start`"
            )

        total_query = await db.execute(select(func.count(Vacancy.vacancy_code)))
        total = total_query.scalar() or 0

        vacancy_query = await db.execute(
            select(Vacancy)
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
                "category": category.title,
                "job_title": vacancy.job_title,
                "company": vacancy.company,
                "working_hours": vacancy.working_hours,
                "job_location_type": vacancy.job_location_type.value,
                "employment_type": vacancy.employment_type.value,
                "country": vacancy.country,
                "city": vacancy.city,
                "salary_min": vacancy.salary_min,
                "salary_max": vacancy.salary_max,
                "currency": vacancy.currency.value,
                "is_salary_public": vacancy.is_salary_public,
                "deadline": vacancy.deadline.isoformat() if vacancy.deadline else None,
                "status": vacancy.status.value,
                "created_at": vacancy.created_at.isoformat() if vacancy.created_at else None,
            }

            vacancy_arr.append(vacancy_obj)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": "Vacancies fetched successfully",
                "vacancy": vacancy_arr
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )