from sqlalchemy import select
from datetime import datetime
from app.models.auth import Auth
from app.core.session import get_db
from app.models.alumni import Alumni
from app.api.v1.schemas.alumni import *
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from app.models.user_photos import UserPhotos
from sqlalchemy.ext.asyncio import AsyncSession

async def get_alumnis(
    start: int = Query(...),
    end: int = Query(...),
    db:  AsyncSession = Depends(get_db)
):
    try:
        total_query = await db.execute(select(Alumni))
        total = len(total_query.scalars().all())

        alumni_query = await db.execute(
            select(Alumni)
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
                "job_title": alumni.job_title,
                "photo": photo.image if photo else None,
                "last_login": auth_user.last_login.isoformat() if auth_user.last_login else None,
                "created_at": alumni.created_at.isoformat() if alumni.created_at else None
            }

            alumni_arr.append(alumni_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Alumnis fetched successfully.",
                "alumnis": alumni_arr,
                "total": total
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
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
            "job_title": alumni.job_title,
            "phone_number": alumni.phone_is_public,
            "registered_city": alumni.registered_city,
            "registered_address": alumni.registered_address,
            "address": alumni.address,
            "address_is_public": alumni.address_is_public,
            "military_obligation": {
                1: "Var",
                2: "Yoxdur",
                3: "Hərbi xidmətə yollanıram",
                4: "Müvəqqəti olaraq getmirəm",
                5: "Digər"
            }.get(alumni.military_obligation, None),
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