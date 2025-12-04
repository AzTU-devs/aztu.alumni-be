from sqlalchemy import select
from app.core.session import get_db
from fastapi import Depends, status
from app.models.vacancy import Vacancy
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.vacancy_requirements import *
from app.models.vacancy_requirements import VacancyRequirement

async def create_requirement(
    request: CreateRequiremt,
    db: AsyncSession = Depends(get_db)
):
    try:
        vacany_query = await db.execute(
            select(Vacancy)
            .where(Vacancy.vacancy_code == request.vacancy_code)
        )

        vacancy = vacany_query.scalar_one_or_none()

        if not vacancy:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Vacancy not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        new_requirement = VacancyRequirement(
            vacancy_code=request.vacancy_code,
            title=request.title
        )

        db.add(new_requirement)
        await db.commit()
        await db.refresh(new_requirement)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "New requirement added succesfuly."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )

async def get_requirements_by_code(
    vacacny_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        vacany_query = await db.execute(
            select(Vacancy)
            .where(Vacancy.vacancy_code == vacacny_code)
        )

        vacancy = vacany_query.scalar_one_or_none()

        if not vacancy:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Vacancy not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        requirement_query = await db.execute(
            select(VacancyRequirement)
            .where(VacancyRequirement.vacancy_code == vacacny_code)
        )

        requirements = requirement_query.scalars().all()

        if not requirements:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "NO CONTENT"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        requirement_arr = []

        for requirement in requirements:
            requirement_obj = {
                "id": requirement.id,
                "vacancy_code": requirement.vacancy_code,
                "title": requirement.title
            }

            requirement_arr.append(requirement_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Requirements fetched successfully.",
                "requirements": requirement_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )