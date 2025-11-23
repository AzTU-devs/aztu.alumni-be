from asyncpg.exceptions import (
    CheckViolationError,
    NotNullViolationError,
    UniqueViolationError
)
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

templates = Jinja2Templates(directory="templates")

ALLOWED_GENDERS = ("Qadın", "Kişi")


ALLOWED_GENDERS = ("Qadın", "Kişi")

async def signup(
    signup_request: Signup,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.email == signup_request.email)
        )

        auth_user = auth_query.scalar_one_or_none()

        if auth_user:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "Email exists"
                }, status_code=status.HTTP_409_CONFLICT
            )
        
        otp = await generate_otp()
        
        new_otp = Otp(
            email=signup_request.email,
            otp_code=int(otp),
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            created_at=datetime.utcnow()
        )

        db.add(new_otp)
        await db.commit()
        await db.refresh(new_otp)
        
        
        subject = "OTP"

        html_content = templates.get_template("/email/otp_verification.html").render({
            "name": signup_request.name,
            "otp_code": otp
        })

        send_html_email(subject, signup_request.email, signup_request.name, html_content)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Otp sent sucessfully.",
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def verify_signup(
    request: Request,
    signup_request: VerifySignup,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth).where(Auth.email == signup_request.email)
        )
        auth_user = auth_query.scalar_one_or_none()
        if auth_user:
            return JSONResponse(
                content={"status_code": 409, "message": "Email already exists."},
                status_code=status.HTTP_409_CONFLICT
            )

        if not is_valid_email(signup_request.email):
            return JSONResponse(
                content={"status_code": 400, "message": "Email is invalid"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if signup_request.gender not in ALLOWED_GENDERS:
            return JSONResponse(
                content={"status_code": 400, "message": f"Gender must be one of {ALLOWED_GENDERS}"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        otp_query = await db.execute(
            select(Otp)
            .where(Otp.email == signup_request.email)
        )

        otp = otp_query.scalar_one_or_none()

        if not otp.otp_code == signup_request.otp:
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "Invalid or expired otp"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if otp.expires_at < datetime.utcnow():
            return JSONResponse(
                content={
                    "status_code": 410,
                    "message": "OTP has expired"
                },
                status_code=status.HTTP_410_GONE
            )

        hashed_password = hash_password(signup_request.password)
        generated_uuid = generate_uuid()

        new_auth = Auth(
            uuid=generated_uuid,
            email=signup_request.email,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow()
        )

        new_alumni = Alumni(
            uuid=generated_uuid,
            name=signup_request.name,
            surname=signup_request.surname,
            father_name=signup_request.father_name,
            gender=signup_request.gender,
            birth_date=signup_request.birth_date,
            created_at=datetime.utcnow(),
            education_degree=signup_request.education_degree,
            start_date=signup_request.start_date,
            end_date=signup_request.end_date
        )

        new_education = Education(
            uuid = generated_uuid,
            university = 'Azərbaycan Texniki Universiteti',
            degree = signup_request.education_degree,
            major = signup_request.major_code,
            start_date = signup_request.start_date,
            end_date = signup_request.end_date,
            gpa = None,
            created_at = datetime.utcnow()
        )

        device_uuid = generate_uuid()
        user_agent_str = request.headers.get("user-agent")
        if user_agent_str:
            user_agent = parse(user_agent_str)
            browser = user_agent.browser.family or "Unknown"
            os = user_agent.os.family or "Unknown"
            device_name = user_agent.device.family or "Unknown"
            is_mobile = user_agent.is_mobile
        else:
            browser = "Unknown"
            os = "Unknown"
            device_name = "Unknown"
            is_mobile = False
        ip = request.client.host if request.client else None

        location = None
        if ip and ip not in ("127.0.0.1", "localhost"):
            try:
                async with httpx.AsyncClient() as client:
                    geo_res = await client.get(f"https://ipapi.co/{ip}/json/")
                    geo_data = geo_res.json()
                    city = geo_data.get("city")
                    region = geo_data.get("region")
                    country = geo_data.get("country_name")
                    if city or region or country:
                        location = ", ".join([part for part in [city, region, country] if part])
            except Exception:
                location = None

        now = datetime.utcnow()

        new_device = AuthUserDevice(
            uuid=device_uuid,
            user_uuid=generated_uuid,
            device_id=device_uuid,
            user_agent=user_agent_str or "Unknown",
            device_name=device_name,
            browser=browser,
            os=os,
            ip=ip,
            location=location,
            is_mobile=is_mobile,
            first_used_at=now,
            last_used_at=now,
            is_blacklisted=False
        )

        db.add(new_auth)
        db.add(new_alumni)
        db.add(new_device)
        db.add(new_education)
        await db.delete(otp)
        await db.commit()
        await db.refresh(new_auth)
        await db.refresh(new_alumni)
        await db.refresh(new_device)
        await db.refresh(new_education)

        return JSONResponse(
            content={"status_code": 201, "message": "Alumni signed up successfully."},
            status_code=status.HTTP_201_CREATED
        )

    except IntegrityError as e:
        await db.rollback()
        orig = e.orig
        if isinstance(orig, NotNullViolationError):
            message = f"Missing required field: {orig.column_name}"
            code = 400
        elif isinstance(orig, CheckViolationError):
            message = f"Check constraint failed: {orig.constraint_name}"
            code = 400
        elif isinstance(orig, UniqueViolationError):
            message = f"Duplicate value for: {orig.column_name}"
            code = 409
        else:
            message = str(e)
            code = 400
        return JSONResponse(
            content={"status_code": code, "error": message},
            status_code=code
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=500
        )

async def signin(
    signin_request: Signin,
    db: AsyncSession
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.email == signin_request.email)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if not verify_password(signin_request.password, auth_user.password_hash):
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        alumni_query = await db.execute(
            select(Alumni)
            .where(Alumni.uuid == auth_user.uuid)
        )

        alumni = alumni_query.scalar_one_or_none()

        auth_user.last_login = datetime.utcnow()

        await db.commit()
        await db.refresh(auth_user)

        alumni_obj = {
            "uuid": str(alumni.uuid),
            "name": alumni.name,
            "surname": alumni.surname,
            "father_name": alumni.father_name,
            "email": auth_user.email,
            "fin_code": alumni.fin_code
        }

        token = encode_auth_token(str(auth_user.uuid), auth_user.is_verified, auth_user.is_verified)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "AUTHORIZED",
                "token": token,
                "alumni": alumni_obj
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )