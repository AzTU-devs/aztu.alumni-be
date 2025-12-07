from asyncpg.exceptions import (
    CheckViolationError,
    NotNullViolationError,
    UniqueViolationError
)
import os
from sqlalchemy import select
from user_agents import parse
from datetime import datetime
from app.util.password import *
from app.models.auth import Auth
from app.util.validator import *
from app.core.session import get_db
from app.models.alumni import Alumni
from app.util.uuid import generate_uuid
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from app.util.jwt import encode_auth_token
from fastapi import UploadFile, File, Form
from app.api.v1.schemas.user_photos import *
from app.models.user_photos import UserPhotos
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, Query, Request
from app.models.auth_user_device import AuthUserDevice

async def upload_image(
    uuid: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth).where(Auth.uuid == uuid)
        )
        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "uuid is invalid"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        folder_path = f"static/user-profiles/{uuid}"
        os.makedirs(folder_path, exist_ok=True)

        file_location = os.path.join(folder_path, "image.png")
        with open(file_location, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)

        # Check if a user photo already exists
        query = await db.execute(select(UserPhotos).where(UserPhotos.uuid == uuid))
        existing_photo = query.scalar_one_or_none()

        if existing_photo:
            # Replace existing image path and update timestamp
            existing_photo.image = file_location
            existing_photo.updated_at = datetime.utcnow()
            db.add(existing_photo)
        else:
            # Create new record
            new_user_photo = UserPhotos(
                uuid=uuid,
                image=file_location,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_user_photo)

        await db.commit()
        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Profile image uploaded successfully"
            },
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse(
            content={
                "status_code": 500,
                "message": f"An error occurred: {str(e)}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
async def delete_user_photo(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(
            select(UserPhotos).where(UserPhotos.uuid == uuid)
        )
        user_photo = query.scalar_one_or_none()

        if not user_photo:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User photo not found"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        import shutil
        if os.path.exists(user_photo.image):
            shutil.rmtree(user_photo.image)

        await db.delete(user_photo)
        await db.commit()

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "User photo deleted successfully"
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "message": f"An error occurred: {str(e)}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )