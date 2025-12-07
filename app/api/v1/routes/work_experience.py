from app.core.database import get_db
from fastapi import APIRouter, Depends
from app.services.work_experience import *
from app.util.limiter import create_limiter
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.work_experience import *
from app.util.jwt_required import token_required
from app.util.current_user_dependency import get_current_user

router = APIRouter()

@router.get("/{uuid}")
async def get_experience_by_uuid_endpoint(
    uuid: str,
    current_user: dict = Depends(get_current_user),
    user = Depends(token_required([1, 2, 3])),
    _ = create_limiter(times=20, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )

    return await get_experience_by_uuid(
        uuid=uuid,
        db=db
    )

@router.post("/create")
async def create_experience_endpoint(
    experience_request: CreateExperience,
    current_user: dict = Depends(get_current_user),
    user = Depends(token_required([1, 2, 3])),
    _ = create_limiter(times=10, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != experience_request.uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )
    
    return await create_experience(
        request=experience_request,
        db=db
    )