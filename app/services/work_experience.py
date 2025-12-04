from sqlalchemy import select
from datetime import datetime
import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from app.util.password import *
from app.models.auth import Auth
from app.util.validator import *
from app.core.session import get_db
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from app.models.education import Education
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.work_experience import *
from app.models.work_experience import WorkExperience

logger = logging.getLogger("work_experience")
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"422 Validation Error on {request.url} | Body: {await request.body()} | Errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "status_code": 422,
            "message": "Validation error",
            "details": jsonable_encoder(exc.errors())
        }
    )

async def create_experience(
    request: CreateExperience,
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"CreateExperience request received: {request.dict() if hasattr(request, 'dict') else request}")
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == request.uuid)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            logger.warning(f"UUID not found while creating experience: {request.uuid}")
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        new_experience = WorkExperience(
            uuid=request.uuid,
            company=request.company,
            job_title=request.job_title,
            start_date=request.start_date,
            end_date=request.end_date,
            employment_type=request.employment_type,
            job_location_type=request.job_location_type,
            description=request.description if request.description else None,
            created_at=datetime.utcnow()
        )

        db.add(new_experience)
        await db.commit()
        await db.refresh(new_experience)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Work experience created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        logger.exception(f"Error while creating work experience. Payload: {request.dict() if hasattr(request, 'dict') else request}")
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_experience_by_uuid(
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
        
        experience_query = await db.execute(
            select(WorkExperience)
            .where(WorkExperience.uuid == uuid)
            .order_by(WorkExperience.start_date.desc(), WorkExperience.end_date.desc())
        )

        experiences = experience_query.scalars().all()

        if not experiences:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "NO CONTENT"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        experience_arr = []

        for experience in experiences:
            experience_arr.append({
                "job_title": experience.job_title,
                "company": experience.company,
                "start_date": experience.start_date.strftime("%d/%m/%Y"),
                "end_date": experience.end_date.strftime("%d/%m/%Y"),
                "employment_type": experience.employment_type,
                "job_location_type": experience.job_location_type,
                "description": experience.description if experience.description else None
            })
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Education fetched successfully.",
                "experiences": experience_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )