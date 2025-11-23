from sqlalchemy import select
from datetime import datetime
from app.util.password import *
from app.models.auth import Auth
from app.util.validator import *
from app.core.session import get_db
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from app.api.v1.schemas.education import *
from app.models.education import Education
from sqlalchemy.ext.asyncio import AsyncSession

async def create_education(
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == education_request.uuid)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        new_education = Education(
            uuid=education_request.uuid,
            university=education_request.university,
            degree=education_request.degree,
            major=education_request.major,
            start_date=education_request.start_date,
            end_date=education_request.end_date,
            gpa=education_request.gpa,
            created_at=datetime.utcnow()
        )

        db.add(new_education)
        await db.commit()
        await db.refresh(new_education)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Education created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_education_by_uuid(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == uuid)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        education_query = await db.execute(
            select(Education)
            .where(Education.uuid == uuid)
            .order_by(Education.start_date.desc(), Education.end_date.desc())
        )

        educations = education_query.scalars().all()

        if not educations:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "NO CONTENT"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        education_arr = []

        for education in educations:
            education_arr.append({
                "university": education.university,
                "degree": education.degree,
                "major": education.major,
                "start_date": education.start_date.strftime("%d/%m/%Y"),
                "end_date": education.end_date.strftime("%d/%m/%Y") if education.end_date else None,
                "gpa": education.gpa
            })
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Education fetched successfully.",
                "education": education_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )