from app.core.database import get_db
from app.services.user_photos import *
from fastapi import APIRouter, Depends
from fastapi import UploadFile, File, Form
from app.util.limiter import create_limiter
from app.api.v1.schemas.user_photos import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.util.jwt_required import token_required
from app.util.current_user_dependency import get_current_user

router = APIRouter()

router = APIRouter()

@router.post("/upload")
async def upload_user_profile_endpoint(
    uuid: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    _ = create_limiter(times=10, seconds=60),
    user = Depends(token_required([1, 2, 3])),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )
    
    return await upload_image(
        uuid=uuid,
        file=file,
        db=db
    )