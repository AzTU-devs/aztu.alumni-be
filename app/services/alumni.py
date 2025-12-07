from sqlalchemy import select, or_
from sqlalchemy.sql import func
from datetime import datetime
from app.models.auth import Auth
from app.core.session import get_db
from app.models.alumni import Alumni
from app.api.v1.schemas.alumni import *
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from app.models.user_photos import UserPhotos
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json
import redis.asyncio as redis

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

redis_client = None

async def get_redis():
    global redis_client
    if not redis_client:
        redis_client = redis.from_url(
            "redis://localhost:6379",
            decode_responses=True
        )
    return redis_client

CACHE_TTL_SECONDS = None  # Cache will persist until manually cleared

async def get_alumnis(
    start: int = Query(...),
    end: int = Query(...),
    search: str | None = Query(default=None),
    db:  AsyncSession = Depends(get_db)
):
    try:
        redis_conn = await get_redis()

        cache_key = f"alumnis:{start}:{end}:{search}"

        cached_data = await redis_conn.get(cache_key)

        if cached_data:
            return JSONResponse(
                content=json.loads(cached_data),
                status_code=status.HTTP_200_OK
            )
        base_query = select(Alumni)

        if search:
            normalized_search = search.lower().replace("-", "").replace(" ", "")
            base_query = base_query.where(
                or_(
                    func.replace(func.replace(func.lower(Alumni.name), '-', ''), ' ', '').like(f"%{normalized_search}%"),
                    func.replace(func.replace(func.lower(Alumni.surname), '-', ''), ' ', '').like(f"%{normalized_search}%"),
                    func.replace(func.replace(func.lower(Alumni.father_name), '-', ''), ' ', '').like(f"%{normalized_search}%"),
                    func.lower(Alumni.fin_code).like(f"%{search.lower()}%"),
                    func.lower(Alumni.job_title).like(f"%{search.lower()}%")
                )
            )

        total_query = await db.execute(base_query)
        total = len(total_query.scalars().all())

        alumni_query = await db.execute(
            base_query
            .offset(start)
            .limit(end - start)
        )

        alumnis = alumni_query.scalars().all()

        if not alumnis:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "no content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )

        alumni_arr = []

        for alumni in alumnis:
            auth_query = await db.execute(
                select(Auth)
                .where(Auth.uuid == alumni.uuid)
            )

            auth_user = auth_query.scalar_one_or_none()

            photo_query = await db.execute(
                select(UserPhotos)
                .where(UserPhotos.uuid == alumni.uuid)
            )

            photo = photo_query.scalar_one_or_none()

            military_map = {
                1: "completed",
                2: "not_done",
                3: "going_to_service",
                4: "temporarily_not_going",
                5: "other"
            }

            alumni_obj = {
                "uuid": str(alumni.uuid),
                "name": alumni.name,
                "surname": alumni.surname,
                "father_name": alumni.father_name,
                "fin_code": alumni.fin_code,
                "email": auth_user.email,
                "is_active": auth_user.is_active,
                "military_obligation": military_map.get(alumni.military_obligation, None),
                "photo": photo.image if photo else None,
                "last_login": auth_user.last_login.isoformat() if auth_user.last_login else None,
                "created_at": alumni.created_at.isoformat() if alumni.created_at else None
            }

            alumni_arr.append(alumni_obj)
        
        response_payload = {
            "status_code": 200,
            "message": "Alumnis fetched successfully.",
            "alumnis": alumni_arr,
            "total": total
        }

        if CACHE_TTL_SECONDS:
            await redis_conn.setex(
                cache_key,
                CACHE_TTL_SECONDS,
                json.dumps(response_payload, default=str)
            )
        else:
            await redis_conn.set(
                cache_key,
                json.dumps(response_payload, default=str)
            )

        return JSONResponse(
            content=response_payload,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        await db.rollback()
        error_message = str(e)

        if "phone_number" in error_message:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "This phone number is already used by another alumni."
                },
                status_code=status.HTTP_409_CONFLICT
            )
        elif "fin_code" in error_message:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "This FIN code is already used by another alumni."
                },
                status_code=status.HTTP_409_CONFLICT
            )

        return JSONResponse(
            content={
                "status_code": 500,
                "error": error_message
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_alumni_by_uuid(
    uuid: str,
    db:  AsyncSession = Depends(get_db)
):
    try:
        alumni_query = await db.execute(
            select(Alumni)
            .where(Alumni.uuid == uuid)
        )

        alumni = alumni_query.scalar_one_or_none()

        auth_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == uuid)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not alumni:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        photo_query = await db.execute(
            select(UserPhotos)
            .where(UserPhotos.uuid == uuid)
        )

        photo = photo_query.scalar_one_or_none()
        
        alumni_obj = {
            "name": alumni.name,
            "surname": alumni.surname,
            "father_name": alumni.father_name,
            "fin_code": alumni.fin_code,
            "email": auth_user.email,
            "gender": alumni.gender,
            "birth_date": alumni.birth_date.isoformat() if alumni.birth_date else None,
            "phone_number": alumni.phone_number,
            "phone_is_public": alumni.phone_is_public,
            "registered_city": alumni.registered_city,
            "registered_address": alumni.registered_address,
            "address": alumni.address,
            "job_title": alumni.job_title if alumni.job_title else None,
            "address_is_public": alumni.address_is_public,
            "military_obligation": alumni.military_obligation,
            "married": alumni.married,
            "photo": photo.image if photo else None,
            "created_at": alumni.created_at.isoformat() if alumni.created_at else None,
            "updated_at": alumni.updated_at.isoformat() if alumni.updated_at else None,
            "is_active": auth_user.is_active,
            "last_login": auth_user.last_login.isoformat() if auth_user.last_login else None
        }

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Alumni details fetched.",
                "alumni": alumni_obj,
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        await db.rollback()
        logger.exception("Error updating alumni profile") 
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def complete_profile(
    request: CompleteProfile,
    db:  AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == request.uuid)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        alumni_query =  await db.execute(
            select(Alumni)
            .where(Alumni.uuid == request.uuid)
        )

        alumni = alumni_query.scalar_one_or_none()

        if not alumni:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Alumni not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        phone_check = await db.execute(
            select(Alumni)
            .where(Alumni.phone_number == request.phone_number)
            .where(Alumni.uuid != request.uuid)
        )
        if phone_check.scalar_one_or_none():
            return JSONResponse(
                status_code=409,
                content={"status_code": 409, "message": "This phone number is already used by another alumni."}
            )

        # Same for FIN code
        fin_check = await db.execute(
            select(Alumni)
            .where(Alumni.fin_code == request.fin_code)
            .where(Alumni.uuid != request.uuid)
        )
        if fin_check.scalar_one_or_none():
            return JSONResponse(
                status_code=409,
                content={"status_code": 409, "message": "This FIN code is already used by another alumni."}
            )

        alumni.name = request.name
        alumni.surname = request.surname
        alumni.father_name = request.father_name
        alumni.phone_number = request.phone_number
        alumni.phone_is_public = request.phone_is_public
        alumni.fin_code = request.fin_code
        alumni.job_title = request.job_title
        alumni.registered_city = request.registered_city
        alumni.registered_address = request.registered_address
        alumni.address = request.address
        alumni.address_is_public = request.address_is_public
        alumni.military_obligation = request.military_obligation
        alumni.married = request.married
        alumni.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(alumni)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Profile completed successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def create_alumni(
    request: AlumniCreate,
    db:  AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == request.uuid)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        alumni_query =  await db.execute(
            select(Alumni)
            .where(Alumni.uuid == request.uuid)
        )

        alumni = alumni_query.scalar_one_or_none()

        if alumni:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "User details for this uuid already exists."
                }, status_code=status.HTTP_409_CONFLICT
            )
        
        new_alumni = Alumni(
            uuid = request.uuid,
            name = request.name,
            surname = request.surname,
            father_name = request.father_name,
            gender = request.gender,
            birth_date = request.birth_date,
            phone_is_public = False,
            address_is_public = False,
            created_at = datetime.utcnow()
        )

        db.add(new_alumni)
        await db.commit()
        await db.refresh(new_alumni)

        # Clear alumni cache after adding a new alumni
        redis_conn = await get_redis()
        keys = await redis_conn.keys("alumnis:*")
        if keys:
            await redis_conn.delete(*keys)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Alumni records created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_alumni(
    uuid: str,
    db:  AsyncSession = Depends(get_db)
):
    try:
        alumni_query = await db.execute(
            select(Alumni)
            .where(Alumni.uuid == uuid)
        )

        alumni = alumni_query.scalar_one_or_none()

        if not alumni:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.uuid == uuid)
        )

        auth_user = auth_query.scalar_one_or_none()

        await db.delete(alumni)
        await db.delete(auth_user)
        await db.commit()

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Alumni deleted successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )