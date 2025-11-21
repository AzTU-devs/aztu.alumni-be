from app.models.education import Education
import httpx
from sqlalchemy import select
from user_agents import parse
from app.models.otp import Otp
from app.util.password import *
from app.models.auth import Auth
from app.util.validator import *
from app.core.session import get_db
from app.models.alumni import Alumni
from app.util.otp import generate_otp
from app.api.v1.schemas.auth import *
from app.api.v1.schemas.alumni import *
from app.util.uuid import generate_uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from app.util.jwt import encode_auth_token
from app.util.email import send_html_email
from app.models.education import Education
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, Query, Request
from app.models.auth_user_device import AuthUserDevice

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
            education_obj = {
                "university": education.university,
                "degree": education.degree,
                "major": education.major,
                "start_date": education.start_date.isoformat(),
                "end_date": education.end_date.isoformat() if education.end_date else None,
                "gpa": education.gpa
            }

            education_arr.append(education_obj)
        
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