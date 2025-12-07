from app.services.alumni import *
from app.core.database import get_db
from app.util.limiter import create_limiter
from sqlalchemy.ext.asyncio import AsyncSession
from app.util.jwt_required import token_required
from app.api.v1.schemas.alumni import AlumniCreate
from fastapi import APIRouter, Depends, Query, HTTPException
from app.util.current_user_dependency import get_current_user

router = APIRouter()


@router.get("/all")
async def get_alumnis_endpoint(
    start: int = Query(...),
    end: int = Query(...),
    search: str | None = Query(default=None),
    _ = create_limiter(times=10, seconds=60),
    user = Depends(token_required([1, 2, 3])),
    db: AsyncSession = Depends(get_db)
):
    return await get_alumnis(
        start=start,
        end=end,
        search=search,
        db=db
    )

@router.get("/{uuid}/details")
async def get_alumnis_endpoint(
    uuid: str,
    current_user: dict = Depends(get_current_user),
    user = Depends(token_required([1, 2, 3])),
    _ = create_limiter(times=10, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )

    return await get_alumni_by_uuid(
        uuid=uuid,
        db=db
    )

@router.post("/create")
async def create_alumni_endpoint(
    request: AlumniCreate,
    user = Depends(token_required([1, 2, 3])),
    current_user: dict = Depends(get_current_user),
    _ = create_limiter(times=10, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != request.uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )
    
    return await create_alumni(
        request=request,
        db=db
    )

@router.post("/complete")
async def complete_profile_endpoint(
    request: CompleteProfile,
    user = Depends(token_required([1, 2, 3])),
    current_user: dict = Depends(get_current_user),
    _ = create_limiter(times=10, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    if current_user["uuid"] != request.uuid:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this user's details."
        )
    return await complete_profile(
        request=request,
        db=db
    )

@router.delete("/{uuid}/delete")
async def delete_alumni_endpoint(
    uuid: str,
    user = Depends(token_required([2, 3])),
    _ = create_limiter(times=5, seconds=60),
    db: AsyncSession = Depends(get_db)
):
    return await delete_alumni(
        uuid=uuid,
        db=db
    )