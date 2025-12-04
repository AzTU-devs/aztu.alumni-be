from app.services.alumni import *
from app.core.database import get_db
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.alumni import AlumniCreate

router = APIRouter()


@router.get("/all")
async def get_alumnis_endpoint(
    start: int = Query(...),
    end: int = Query(...),
    search: str | None = Query(default=None),
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
    db: AsyncSession = Depends(get_db)
):
    return await get_alumni_by_uuid(
        uuid=uuid,
        db=db
    )

@router.post("/create")
async def create_alumni_endpoint(
    request: AlumniCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_alumni(
        request=request,
        db=db
    )

@router.post("/complete")
async def complete_profile_endpoint(
    request: CompleteProfile,
    db: AsyncSession = Depends(get_db)
):
    return await complete_profile(
        request=request,
        db=db
    )

@router.delete("/{uuid}/delete")
async def delete_alumni_endpoint(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    return await delete_alumni(
        uuid=uuid,
        db=db
    )