from fastapi import UploadFile, File
from app.core.database import get_db
from app.services.user_photos import *
from fastapi import APIRouter, Depends
from app.api.v1.schemas.user_photos import *
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/upload")
async def upload_user_profile_endpoint(
    uuid: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await upload_image(
        uuid=uuid,
        file=file,
        db=db
    )